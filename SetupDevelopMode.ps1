. ..\buildtools\build_func.ps1

Set-PythonPath @("..\buildtools")

Set-Location "./Source"

Invoke-Expression "python.exe setup.py develop"