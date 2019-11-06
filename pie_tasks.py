import os
import shutil

try:
    import winreg
except ImportError as ie:
    # probably running on python2
    import _winreg as winreg

from pie import *
from pie import CmdContext, CmdContextManager

@task
def build():
    with venv(".venvs\\build"):
        cmd(r'python setup.py bdist_wheel clean --all')


@task
def setup():
    createVenvs()
    updatePackages()


@task
def createVenvs():
    python2_path = os.path.join(get_arcpy2_python_path(), "Python.exe")

    create_venv(python2_path, ".venvs\\build")
    create_venv(python2_path, ".venvs\\test-py2")

    remove_dir(".venvs\\test-py3")
    conda(".venvs\\test-py3", get_arcgis_pro_conda_path()).clone("arcgispro-py3", extraArguments="--copy --no-shortcuts --offline")


@task
def updatePackages():
    with venv(".venvs\\build"):
        pip(r'install -U pip')
        pip(r'install -U -r requirements.build.txt')
        pip(r'install -U -r requirements.txt')

    with venv(".venvs\\test-py2"):
        pip(r'install -U pip')
        pip(r'install -U -r requirements.build.txt')
        pip(r'install -U -r requirements.test.txt')
        pip(r'install -U -r requirements.txt')
        cmd(r'python setup.py develop')

    with conda(".venvs\\test-py3", get_arcgis_pro_conda_path()):
        pip(r'install -U pip')
        pip(r'install -r requirements.build.txt')
        pip(r'install -r requirements.test.txt')
        pip(r'install -r requirements.txt')
        cmd(r'python setup.py develop')


@task
def test():
    with venv(".venvs\\test-py2"):
        cmd("python -m pytest tests --cov=arcpyext --cov-report=")

    with conda(".venvs\\test-py3", get_arcgis_pro_conda_path()):
        cmd("python -m pytest tests --cov=arcpyext --cov-append --cov-report=term --cov-report=html")


@task([OptionsParameter('version')])
def upload(version):
    with venv(".venvs\\build"):
        cmd(r'python -m twine check dist\arcpyext-{}-py2.py3-none-any.whl'.format(version))
        cmd(r'python -m twine upload dist\arcpyext-{}-py2.py3-none-any.whl'.format(version))


class conda(CmdContext):
    """A context class used to execute commands within a conda environment"""
    def __init__(self, path, conda_path):
        self.conda_path = os.path.abspath(conda_path)
        self.path = os.path.abspath(path)

    def clone(self, env_to_clone, extraArguments=''):
        """Creates a conda environment by running conda and cloning an existing named environment."""
        cmd(r'"{}" create {} --prefix "{}" --clone "{}"'.format(self.conda_path, extraArguments, self.path, env_to_clone))

    def cmd(self, c):
        """Runs the command `c` in this conda environment."""
        activate_path = os.path.join(os.path.dirname(self.conda_path), "activate.bat")
        scripts_path = os.path.join(self.path, "Scripts")

        c = 'cmd /v /c ""{}" && set PATH={};{};!PATH! && {}"'.format(activate_path, self.path, scripts_path, c)

        return CmdContextManager.cmd(c, self.contextPosition)


def create_venv(python_path, venv_path):
    remove_dir(venv_path)

    cmd("\"{}\" -m virtualenv \"{}\" --system-site-packages".format(python_path, venv_path))


def get_arcpy2_python_path():
    # open the registry at HKEY_LOCAL_MACHINE
    hklm_key = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)

    try:
        # get root ArcGIS key
        arcgis_key = winreg.OpenKey(hklm_key, "SOFTWARE\\ESRI\\ArcGIS", 0, winreg.KEY_READ | winreg.KEY_WOW64_32KEY)

        # get installed version, split into parts
        version_info = winreg.QueryValueEx(arcgis_key, "RealVersion")[0].split(".")

        # Use 32-bit version
        return _get_python2_path(hklm_key, "ArcGIS", version_info[0], version_info[1],
                                 winreg.KEY_READ | winreg.KEY_WOW64_32KEY)
    finally:
        # close the registry
        winreg.CloseKey(hklm_key)


def get_arcgis_pro_conda_path():
    return os.path.join(_get_arcgis_pro_conda_root_path(), r"Scripts\conda.exe")


def remove_dir(venv_path):
    if os.path.isdir(venv_path):
        shutil.rmtree(venv_path)


def _get_arcgis_pro_conda_root_path():
    # open the registry at HKEY_LOCAL_MACHINE
    hklm_key = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)

    try:
        # attempt to get the ArcGIS Pro installation details
        arcgis_pro_key = winreg.OpenKey(hklm_key, "SOFTWARE\\ESRI\\ArcGISPro", 0,
                                        winreg.KEY_READ | winreg.KEY_WOW64_64KEY)
        env_name = winreg.QueryValueEx(arcgis_pro_key, "PythonCondaEnv")[0]
        install_root = winreg.QueryValueEx(arcgis_pro_key, "PythonCondaRoot")[0]
        winreg.CloseKey(arcgis_pro_key)
    except WindowsError as we:
        raise Exception("ArcGIS Pro not installed.")
    finally:
        # close the registry
        winreg.CloseKey(hklm_key)
    
    return os.path.normpath(install_root)


def _get_python2_path(hklm_key, install_name, major_version, minor_version, sam):
    # format ArcGIS Desktop python key path from version info, get key
    python_desktop_key_path = "SOFTWARE\\ESRI\\Python{0}.{1}".format(major_version, minor_version)

    python_desktop_key = None
    try:
        python_desktop_key = winreg.OpenKey(hklm_key, python_desktop_key_path, 0, sam)
        python_root = winreg.QueryValueEx(python_desktop_key, "PythonDir")[0]
        return os.path.join(python_root, "{0}{1}.{2}".format(install_name, major_version, minor_version))
    finally:
        if python_desktop_key:
            winreg.CloseKey(python_desktop_key)
