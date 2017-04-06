from __future__ import print_function
"""
pie - Python Interactive Executor
Enables a user to execute predefined tasks that may accept parameters and options from the command line without any other required packages.
Great for bootstrapping a development environment, and then interacting with it.
"""
__VERSION__='0.1.3'


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
# function to execute a command - must emulate the subprocess call method
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
    """
    A callable wrapper around a task function. Provides prompting for missing function arguments.
    """
    def __init__(self,fn,params):
        self.fn=fn
        self.params=params
        self.desc=fn.__doc__

        # parameters set when registering tasks
        self.hidden=False

    def __call__(self,*args,**kwargs):
        # args might be a tuple, but we want to append to it
        args=list(args)
        # go through parameters and make sure we have arguments for each, otherwise inject or prompt for them
        for i,p in enumerate(self.params):
            if len(args)<=i:
                kwargs[p.name]=p.getValue()
            else:
                args[i]=p.convertValue(args[i])
        return self.fn(*args,**kwargs)


def task(parameters=[]):
    """
    A (function that returns a) decorator that converts a simple Python function into a pie Task.
     - parameters is a list of objects (use Lookup) with the following attributes:
         name - name of the parameter
         conversionFn - a function that will take a string and convert it to the desired type
    """
    def decorator(taskFn):
        # convert the function into a callable task instance
        return TaskWrapper(taskFn,parameters)

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
            tasks[modulePrefix+k]=v

        elif isinstance(v,types.ModuleType):
            # there is a situation where a module in a package that is imported into another module (so, doubly nested tasks) will also show up at the package level, even though it's not imported there
            # eg. pie_tasks/__init__.py does "from . import submodule", submodule does "from . import doubleNest", but this also causes doubleNest to show up in pie_tasks
            # I can't figure out any way to distinguish the difference, but, at the moment, I think it's an obscure enough situation to not worry about yet
            # Actually, we have to keep a list of modules we've traversed so that we don't recurse forever (circular imports), this will remove the above problem, but may not fix it correctly...
            if v not in alreadyTraversed:
                alreadyTraversed.add(v)
                registerTasksInModule(modulePrefix+k,v)


def importTasks(moduleName='pie_tasks'):
    """Import the pie_tasks module and register all tasks found"""
    m=__import__(moduleName)
    registerTasksInModule('',m)



# ----------------------------------------
# parameters to tasks
# ----------------------------------------
class Parameter(object):
    def __init__(self,name,prompt=None,inputFn=INPUT_FN,conversionFn=lambda o:o):
        self.name=name
        self.prompt=prompt
        self.inputFn=inputFn
        self.conversionFn=conversionFn

    # add a value property that calls getValue which can then be overridden.
    @property
    def value(self):
        return self.getValue()

    def getValue(self):
        # TODO: provide a default value when prompting the user - would be best to use the default value as provided with the function definition, rather than add a 'default' attribute.
        # prompt for the value
        promptStr=self.prompt if self.prompt else 'Please enter a value for {}: '.format(self.name)
        v=self.inputFn(promptStr)
        return self.convertValue(v)

    def convertValue(self,v):
        """This is separate so that getValue is only used for missing arguments, but convertValue is used for arguments provided on the command line too."""
        return self.conversionFn(v)


class OptionsParameter(Parameter):
    """A parameter that is asked for once (or provided on the command line) and then this value is stored in options and used wherever else an OptionsParameter of the same name is referenced."""
    NO_VALUE=object()

    def getValue(self):
        v=getattr(options,self.name,self.NO_VALUE)
        if v is self.NO_VALUE:
            v=super(OptionsParameter,self).getValue()
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

    @classmethod
    def enter(cls,ctx):
        cls.context.append(ctx)
        return len(cls.context)-1

    @classmethod
    def cmd(cls,c,i=None):
        if i is None: i=len(cls.context)
        if i>0: return cls.context[i-1].cmd(c)
        CMD_FN(c,shell=True)

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
    """
    A context class used to execute commands within a virtualenv
    """
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


class CreateBatchFile(Argument):
    def execute(self):
        pythonHome=os.environ.get('PYTHONHOME','')
        pythonExe=sys.executable
        if WINDOWS:
            with open('pie.bat','w') as fout:
                fout.write('@echo off\n')
                if pythonHome:
                    fout.write('set PIE_OLD_PYTHONHOME=%PYTHONHOME%\n')
                    fout.write('set PIE_OLD_PATH=%PATH%\n')
                    fout.write('set PYTHONHOME={}\n'.format(pythonHome))
                    fout.write('set PATH={};%PATH%\n'.format(pythonHome))
                fout.write('"{}" -m pie %*\n'.format(pythonExe))
                if pythonHome:
                    fout.write('set PYTHONHOME=%PIE_OLD_PYTHONHOME%\n')
                    fout.write('set PATH=%PIE_OLD_PATH%\n')
                    fout.write('set PIE_OLD_PYTHONHOME=\n')
                    fout.write('set PIE_OLD_PATH=\n')
        else:
            with open('pie','w') as fout:
                if pythonHome:
                    fout.write('export PIE_OLD_PYTHONHOME=$PYTHONHOME\n')
                    fout.write('export PIE_OLD_PATH=$PATH\n')
                    fout.write('export PYTHONHOME={}\n'.format(pythonHome))
                    fout.write('export PATH={}:$PATH\n'.format(pythonHome))
                fout.write('"{}" -m pie %*\n'.format(pythonExe))
                if pythonHome:
                    fout.write('export PYTHONHOME=$PIE_OLD_PYTHONHOME\n')
                    fout.write('export PATH=$PIE_OLD_PATH\n')
                    fout.write('unset PIE_OLD_PYTHONHOME\n')
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
        print('Usage:    pie [ -v | -h | -b | -l | -L ]')
        print('          pie [ -o <name>=<value> | <task>[(<args>...)] ]...')
        print('Version:  v{}'.format(__VERSION__))
        print('')
        print('  -v      Display version')
        print('  -h      Display this help')
        print('  -b      Create batch file shortcut')
        print('  -l      List available tasks with description')
        print('  -L      List available tasks with name only')
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
            elif arg=='-o':
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
# entry point
# ----------------------------------------
def main(args):
    args=parseArguments(args)
    if args:
        tasksImported=False
        for a in args:
            # only import tasks if needed, saves exceptions when only looking for help or creating the batch file
            if a.needsTasksImported and not tasksImported:
                try:
                    importTasks()
                except Exception as e:
                    # pick up the specific case of not being able to find a pie_tasks module/package
                    if isinstance(e,ImportError) and e.message=='No module named pie_tasks':
                        print('pie_tasks could not be found.')
                    else:
                        print('An error occurred when importing pie_tasks:\n'+traceback.format_exc())
                    break
                tasksImported=True
            # try to execute the arg
            try:
                a.execute()
            except TaskCall.TaskNotFound as e:
                print('Task {} could not be found.'.format(e.name))
                break
            # print(repr(a))
    else:
        Help().execute()


if __name__=='__main__':
    # import pie so that both we and any pie_tasks code that imports pie are referring to the same module variables
    import pie
    # skip the name of the command
    pie.main(sys.argv[1:])
