from __future__ import print_function
"""
pie - Python Interactive Executor
Enables a user to execute predefined tasks that may accept parameters and options from the command line without any other required packages.
Great for bootstrapping a development environment, and then interacting with it.
"""
__VERSION__='0.2.6'


import inspect
import os
import re
import subprocess
import sys
import traceback
import types
from functools import wraps


__all__=['task','Parameter','OptionsParameter','options','cmd','pip','venv']


# environment constants
WINDOWS=(os.name=='nt')
PY3=(sys.version_info>=(3,0))

# function for input (also so that we can mock it tests)
INPUT_FN=input if PY3 else raw_input
# function to execute a command - must emulate the subprocess call method and return an error code on failure
CMD_FN=subprocess.call



# ----------------------------------------
# configuration
# ----------------------------------------
class Lookup(object):
    """
    A class that can be used like a dictionary with more succinct syntax:
        l=Lookup(name='example',value='good')
        print(l.name)
        l.newValue=2
    """
    def __init__(self,**entries):
        self.__dict__.update(entries)


# options is a lookup object where predefined options (in code) can be placed, as well as provided on the command line.
options=Lookup()



# ----------------------------------------
# tasks
# ----------------------------------------
# tasks is a dictionary of registered tasks, where key=name. Tasks are possibly from within submodules where name=module.task.
tasks={}


class TaskWrapper(object):
    """A callable wrapper around a task function. Provides prompting for missing function arguments."""
    def __init__(self,fn,params,namespace):
        self.fn=fn
        self.params=params
        self.namespace=namespace
        self.desc=fn.__doc__

        # parameters set when registering tasks
        self.hidden=False

    def __call__(self,*args,**kwargs):
        # get arg names and defaults from the function
        (arg_names,varargs,keywords,defaults)=inspect.getargspec(self.fn)
        # map defaults to an arg name
        defaults=dict(zip(arg_names[len(arg_names)-len(defaults):],defaults)) if defaults is not None else {}
        # map provided values to an arg name
        provided=dict(zip(arg_names[:len(args)],args))
        provided.update(kwargs)

        # for each param, get the value and add to provided if not already there, otherwise make sure it's converted
        for param in self.params:
            if param.name not in arg_names:
                raise Exception('{} not a valid parameter of task {}'.format(param.name,fn.__name__))
            if param.name not in provided:
                # provide a default if one exists
                default=defaults.get(param.name,Parameter.NO_VALUE)
                provided[param.name]=param.getValue(default)
            else:
                provided[param.name]=param.convertValue(provided[param.name])

        return self.fn(**provided)


def task(parameters=[],namespace=None):
    """
    A (function that returns a) decorator that converts a simple Python function into a pie Task.
     - parameters is a list of objects (use Lookup) with the following attributes:
         name - name of the parameter
         conversionFn - a function that will take a string and convert it to the desired type
    """
    def decorator(taskFn):
        # convert the function into a callable task instance
        return TaskWrapper(taskFn,parameters,namespace)

    # check in case we were called as a decorator eg. @task (without the function call)
    if callable(parameters):
        # this means that parameters is actually the function to decorate
        taskFn=parameters
        # but parameters is used in the wrapper and assumed to be a list, so set it as an empty list (as we weren't provided any parameters)
        parameters=[]
        return decorator(taskFn)

    # otherwise return the decorator function
    return decorator


alreadyTraversed=set()
def registerTasksInModule(modulePath,module):
    """Recursively traverse through modules, registering tasks"""
    modulePrefix=(modulePath+'.' if modulePath else '')
    for k,v in vars(module).items():
        if isinstance(v,TaskWrapper):
            if k.startswith('_'): v.hidden=True
            # handle our various namespace options
            k=k.replace('__','.')
            mp=modulePrefix+v.namespace+'.'+k if v.namespace is not None else modulePrefix+k
            tasks[mp]=v

        elif isinstance(v,types.ModuleType):
            # there is a situation where a module in a package that is imported into another module (so, doubly nested tasks) will also show up at the package level, even though it's not imported there
            # eg. pie_tasks/__init__.py does "from . import submodule", submodule does "from . import doubleNest", but this also causes doubleNest to show up in pie_tasks
            # I can't figure out any way to distinguish the difference, but, at the moment, I think it's an obscure enough situation to not worry about yet
            # Actually, we have to keep a list of modules we've traversed so that we don't recurse forever (circular imports), this will remove the above problem, but may not fix it correctly...
            if v not in alreadyTraversed:
                alreadyTraversed.add(v)
                registerTasksInModule(modulePrefix+k,v)


def importTasks():
    """Import the pie_tasks module and register all tasks found"""
    moduleName=getattr(options,'PIE_TASKS_MODULE','pie_tasks')
    m=__import__(moduleName)
    registerTasksInModule('',m)



# ----------------------------------------
# parameters to tasks
# ----------------------------------------
class Parameter(object):
    """Parameter base class for specifying how to handle parameters for tasks"""
    NO_VALUE=object()

    def __init__(self,name,prompt=None,inputFn=NO_VALUE,conversionFn=lambda o:o,use_default=False):
        """
        name - must match the name of the function argument
        prompt - a string that is used if needed to prompt for input
        inputFn - the function to use to prompt for input
        conversionFn - the function used to convert a string to the correct type
        use_default - if True - if the function argument has a default, use it
                      otherwise, suggest the default in the prompt but still prompt, an empty string input will be converted to the default value
        """
        self.name=name
        self.prompt=prompt
        self.inputFn=inputFn if inputFn is not self.NO_VALUE else INPUT_FN
        self.conversionFn=conversionFn
        self.use_default=use_default

    def getValue(self,default):
        """Gets a value for a missing argument, suggesting a default if provided."""
        if default is Parameter.NO_VALUE or self.use_default==False:
            # prompt for the value
            promptStr=self.prompt
            if promptStr is None:
                defaultStr=' (default: {!r})'.format(default) if default is not Parameter.NO_VALUE else ''
                promptStr='Please enter a value for {}{}: '.format(self.name,defaultStr)
            v=self.inputFn(promptStr)
            if default is not Parameter.NO_VALUE and v=='': v=default
        else:
            # self.use_default must be True and self.default must not be Parameter.NO_VALUE
            v=default
        return self.convertValue(v)

    def convertValue(self,v):
        """This is separate so that getValue is only used for missing arguments, but convertValue is used for arguments provided on the command line too."""
        return self.conversionFn(v)


class OptionsParameter(Parameter):
    """A parameter that is asked for once (or provided on the command line) and then this value is stored in options and used wherever else an OptionsParameter of the same name is referenced."""

    def getValue(self,default):
        v=getattr(options,self.name,Parameter.NO_VALUE)
        if v is Parameter.NO_VALUE:
            v=super(OptionsParameter,self).getValue(default)
        return v

    def convertValue(self,v):
        """Whenever a value is converted, make sure that converted value is persisted to options."""
        v=super(OptionsParameter,self).convertValue(v)
        setattr(options,self.name,v)
        return v

# ----------------------------------------
# operations
# ----------------------------------------
class CmdContextManager(object):
    """
    The CmdContextManager (singleton) is used to keep track of what context a command is being executed within:

        with venv('venv/build'):
            cmd('python -m pip')
    """
    context=[]


    class CmdError(Exception):
        def __init__(self,errorcode,cmd):
            self.errorcode=errorcode
            self.cmd=cmd


    @classmethod
    def enter(cls,ctx):
        cls.context.append(ctx)
        return len(cls.context)-1

    @classmethod
    def cmd(cls,c,i=None):
        if i is None: i=len(cls.context)
        if i>0: return cls.context[i-1].cmd(c)
        errorcode=CMD_FN(c,shell=True)
        if errorcode!=0:
            raise cls.CmdError(errorcode,c)

    @classmethod
    def exit(cls):
        cls.context.pop()


def cmd(c):
    """Executes a system command (within the current context)"""
    return CmdContextManager.cmd(c)


def pip(c,pythonCmd='python'):
    """Runs a pip command"""
    cmd('{} -m pip {}'.format(pythonCmd,c))


class CmdContext(object):
    """Base class for all cmd context objects."""
    # make this a context manager
    def __enter__(self):
        self.contextPosition=CmdContextManager.enter(self)
        return self

    def __exit__(self,exc_type,exc_value,traceback):
        CmdContextManager.exit()
        # we don't care about an exception


class venv(CmdContext):
    """A context class used to execute commands within a virtualenv"""
    def __init__(self,path):
        self.path=path

    def create(self,extraArguments='',pythonCmd='python',py3=PY3):
        """Creates a virutalenv by running the `pythonCmd` and adding `extraArguments` if required. `py3` is used to flag whether this python interpreter is py3 or not. Defaults to whatever the current python version is."""
        if py3:
            c=r'{} -m venv {} "{}"'.format(pythonCmd,extraArguments,self.path)
        else:
            c=r'{} -m virtualenv {} "{}"'.format(pythonCmd,extraArguments,self.path)
        cmd(c)

    def cmd(self,c):
        """Runs the command `c` in this virtualenv."""
        if WINDOWS:
            c=r'cmd /c "{}\Scripts\activate.bat && {}"'.format(self.path,c)
        else:
            c=r'bash -c "{}/bin/activate && {}"'.format(self.path,c)
        return CmdContextManager.cmd(c,self.contextPosition)



# ----------------------------------------
# Command line functionality
# ----------------------------------------
class Argument(object):
    # a flag to indicate that tasks must be imported to execute this argument
    needsTasksImported=False

    def execute(self):
        raise NotImplemented()

    def __repr__(self):
        return self.__class__.__name__


class Version(Argument):
    def execute(self):
        print('pie v{}'.format(__VERSION__))

    def __repr__(self):
        return 'Version: {}'.format(__VERSION__)


class CreatePieVenv(Argument):
    def execute(self):
        pv=PieVenv()
        print('Creating {}'.format(pv.PIE_VENV))
        pv.create()


class UpdatePieVenv(Argument):
    def execute(self):
        pv=PieVenv()
        print('Updating {} with {}'.format(pv.PIE_VENV,pv.PIE_REQUIREMENTS))
        pv.update()


class CreateBatchFile(Argument):
    def execute(self):
        pythonHome=os.environ.get('PYTHONHOME','')
        pythonDir=os.path.dirname(sys.executable)
        if WINDOWS:
            with open('pie.bat','w') as fout:
                fout.write('@echo off\n')
                fout.write('set PIE_OLD_PYTHONHOME=%PYTHONHOME%\n')
                fout.write('set PYTHONHOME={}\n'.format(pythonHome))
                fout.write('set PIE_OLD_PATH=%PATH%\n')
                fout.write('set PATH={};%PATH%\n'.format(pythonDir))
                fout.write('python -m pie %*\n')
                fout.write('set PYTHONHOME=%PIE_OLD_PYTHONHOME%\n')
                fout.write('set PIE_OLD_PYTHONHOME=\n')
                fout.write('set PATH=%PIE_OLD_PATH%\n')
                fout.write('set PIE_OLD_PATH=\n')
        else:
            with open('pie','w') as fout:
                fout.write('export PIE_OLD_PYTHONHOME=$PYTHONHOME\n')
                fout.write('export PYTHONHOME={}\n'.format(pythonHome))
                fout.write('export PIE_OLD_PATH=$PATH\n')
                fout.write('export PATH={}:$PATH\n'.format(pythonDir))
                fout.write('python -m pie %*\n')
                fout.write('export PYTHONHOME=$PIE_OLD_PYTHONHOME\n')
                fout.write('unset PIE_OLD_PYTHONHOME\n')
                fout.write('export PATH=$PIE_OLD_PATH\n')
                fout.write('unset PIE_OLD_PATH\n')


class ListTasks(Argument):
    needsTasksImported=True

    def __init__(self,includeDescription=True):
        self.includeDescription=includeDescription

    def execute(self):
        for k in sorted(tasks.keys()):
            v=tasks[k]
            if v.hidden: continue
            if self.includeDescription:
                desc=v.desc or ''
                print('{:30} {:.70}'.format(k,desc.replace('\n',' ')))
            else:
                print(k)


class Help(Argument):
    def execute(self):
        print('Usage:    pie [ -v | -h | -b | -l | -L | m <name> ]')
        print('          pie [ -o <name>=<value> | <task>[(<args>...)] ]...')
        print('Version:  v{}'.format(__VERSION__))
        print('')
        print('  -v      Display version')
        print('  -h      Display this help')
        print('  -b      Create batch file shortcut')
        print('  -l      List available tasks with description')
        print('  -L      List available tasks with name only')
        print('  -m <n>  Change name of the pie_tasks module to import')
        print('  -R      Creates a .venv-pie venv using requirements.pie.txt')
        print('  -r      Updates the .venv-pie venv using requirements.pie.txt')
        print('  -o      Sets an option with name to value')
        print('  <task>  Runs a task passing through arguments if required')
        print('')
        print('The order of -o and <task> options matters - each will be executed in the order given on the command line.')


class Option(Argument):
    def __init__(self,name,value):
        self.name=name
        self.value=value

    def execute(self):
        setattr(options,self.name,self.value)

    def __repr__(self):
        return 'Option: {}={}'.format(self.name,self.value)


class ModuleName(Argument):
    def __init__(self,name):
        self.name=name

    def execute(self):
        setattr(options,'PIE_TASKS_MODULE',self.name)

    def __repr__(self):
        return 'ModuleName: {}'.format(self.name)


class TaskCall(Argument):
    needsTasksImported=True

    class TaskNotFound(Exception):
        def __init__(self,name):
            self.name=name

    def __init__(self,name,args=[],kwargs={}):
        self.name=name
        self.args=args
        self.kwargs=kwargs

    def execute(self):
        if self.name in tasks: tasks[self.name](*self.args,**self.kwargs)
        else: raise self.TaskNotFound(self.name)

    def __repr__(self):
        return 'Task: {}(args={},kwargs={})'.format(self.name,self.args,self.kwargs)



# ----------------------------------------
# Command line parsing
# ----------------------------------------
TASK_RE=re.compile(r'(?P<name>[^()]+)(\((?P<args>.*)\))?')
def parseArguments(args):
    i=0
    parsed=[]
    while i<len(args):
        arg=args[i]
        if arg.startswith('-'):
            # although we say that these options are check that incompatible options aren't used together
            if arg=='-v':
                parsed.append(Version())
            elif arg=='-h':
                parsed.append(Help())
            elif arg=='-b':
                parsed.append(CreateBatchFile())
            elif arg=='-l':
                parsed.append(ListTasks())
            elif arg=='-L':
                parsed.append(ListTasks(includeDescription=False))
            elif arg=='-m':
                parsed.append(ModuleName(args[i+1]))
                i+=1
            elif arg=='-R':
                parsed.append(CreatePieVenv())
                parsed.append(UpdatePieVenv())
            elif arg=='-r':
                parsed.append(UpdatePieVenv())
            elif arg=='-o':
                if '=' not in args[i+1]: raise Exception('Option ("{}") must be in format name=value'.format(args[i+1]))
                name,value=args[i+1].split('=')
                parsed.append(Option(name,value))
                i+=1
            else:
                raise Exception('Unknown argument: {}'.format(arg))
        else:
            mo=TASK_RE.match(arg)
            if mo:
                taskArgs=mo.group('args')
                taskArgs=taskArgs.split(',') if taskArgs else []
                # TODO: add further parsing to handle keyword arguments
                parsed.append(TaskCall(mo.group('name'),args=taskArgs,kwargs={}))
            else:
                raise Exception('Unknown task format: {}'.format(arg))
        i+=1
    return parsed



# ----------------------------------------
# pie venv
# ----------------------------------------
class PieVenv(object):
    PIE_REQUIREMENTS='requirements.pie.txt'
    PIE_VENV='.venv-pie'

    def requirements_exists(self):
        return os.path.isfile(self.PIE_REQUIREMENTS)

    def exists(self):
        return os.path.isdir(self.PIE_VENV)

    def is_activated(self):
        return sys.prefix.endswith(self.PIE_VENV)

    def create(self):
        venv(self.PIE_VENV).create('--system-site-packages')

    def update(self):
        with venv(self.PIE_VENV):
            pip('install -U pip')
            pip('install -r {}'.format(self.PIE_REQUIREMENTS))

    def run_pie(self,args):
        with venv(self.PIE_VENV):
            r=cmd(r'python pie.py {}'.format(' '.join(args)))
        return r



# ----------------------------------------
# entry point
# ----------------------------------------
def main(args):
    parsed_args=parseArguments(args)
    if parsed_args:
        # only import tasks if needed, only run in a pie venv if needed, this saves exceptions and time when only looking for help or creating the batch file
        if any([a.needsTasksImported for a in parsed_args]):
            # run in the pie venv if required
            pv=PieVenv()
            # either no pie requirements or the venv is activated
            if not pv.requirements_exists() or pv.is_activated():
                # import tasks
                try:
                    importTasks()
                except Exception as e:
                    # pick up the specific case of not being able to find a pie_tasks module/package
                    # handle different attributes and messages in py2 vs py3
                    if isinstance(e,ImportError) and (getattr(e,'message','')=='No module named pie_tasks' or getattr(e,'msg','')=="No module named 'pie_tasks'"):
                        print('pie_tasks could not be found.',file=sys.stderr)
                    else:
                        print('An error occurred when importing pie_tasks:\n'+traceback.format_exc(),file=sys.stderr)
                    return 1

            else:
                # otherwise, we need to activate and run pie again, within the venv
                if pv.exists():
                    return pv.run_pie(args)
                else:
                    print('{} not found. You can create it with the -R argument.'.format(pv.PIE_VENV),file=sys.stderr)
                    return 1

        # try to execute each arg
        for a in parsed_args:
            try:
                a.execute()
            except CmdContextManager.CmdError as e:
                print('Error when executing command "{}". Errorcode = {}'.format(e.cmd,e.errorcode),file=sys.stderr)
                return e.errorcode
            except TaskCall.TaskNotFound as e:
                print('Task {} could not be found.'.format(e.name),file=sys.stderr)
                return 1
        return 0

    else:
        Help().execute()
        return 1


if __name__=='__main__':
    # import pie so that both we and any pie_tasks code that imports pie are referring to the same module variables
    import pie
    # skip the name of the command
    sys.exit(pie.main(sys.argv[1:]))
