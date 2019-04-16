from pie import *

@task
def build():
    cmd(r'python setup.py clean --all bdist_wheel')


@task
def setup():
    createVenvs()
    updatePackages()


@task
def createVenvs():
    venv(r'venvs\test').create('--system-site-packages')


@task
def updatePackages():
    with venv(r'venvs\test'):
        pip(r'install -U pip')
        pip(r'install -U -r requirements.txt')
        pip(r'install -U -r requirements.test.txt')


@task
def test():
    with venv(r'venvs\test'):
        cmd(r'python setup.py build')
        cmd(r'pip uninstall -y arcpyext')
        with open('arcpyext/_version.py') as fin: exec(fin)
        cmd(r'pip install dist/arcpyext-{}-py2.py3-none-any.whl'.format(__version__))
        cmd(r'python -m pytest -s tests')


@task([OptionsParameter('version')])
def upload(version):
    cmd(r'python -m twine upload dist\arcpyext-{}-py2-none-any.whl'.format(version))
