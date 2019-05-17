import os
import shutil

try:
    import winreg
except ImportError as ie:
    # probably running on python2
    import _winreg as winreg

from pie import *


@task
def build():
    cmd(r'python setup.py bdist_wheel clean --all')


@task
def setup():
    createVenvs()
    updatePackages()


@task
def createVenvs():
    python2_path = os.path.join(get_arcpy2_python_path(), "Python.exe")
    python3_path = os.path.join(get_arcpy3_python_path(), "Python.exe")

    create_venv(python2_path, ".venvs\\build")
    create_venv(python2_path, ".venvs\\test-py2")
    create_venv(python3_path, ".venvs\\test-py3")


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

    with venv(".venvs\\test-py3"):
        pip(r'install -U pip')
        pip(r'install -U -r requirements.build.txt')
        pip(r'install -U -r requirements.test.txt')
        pip(r'install -U -r requirements.txt')
        cmd(r'python setup.py develop')


@task
def test():
    with venv(".venvs\\test-py2"):
        cmd("python -m pytest tests --ignore=tests\\mp\\ --cov=arcpyext --cov-report=")

    with venv(".venvs\\test-py3"):
        cmd("python -m pytest tests --ignore=tests\\mapping\\ --cov=arcpyext --cov-append --cov-report=term --cov-report=html")


@task([OptionsParameter('version')])
def upload(version):
    cmd(r'python -m twine upload dist\arcpyext-{}-py2-none-any.whl'.format(version))


def create_venv(python_path, venv_path):
    if os.path.isdir(venv_path):
        shutil.rmtree(venv_path)

    cmd("\"{}\" -m virtualenv \"{}\" --system-site-packages".format(python_path, venv_path))


def get_arcpy3_python_path():
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

    return os.path.join(install_root, "envs", env_name)


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