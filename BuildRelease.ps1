Set-Location "./Source"
Invoke-Expression "python.exe setup.py sdist"
Invoke-Expression "python.exe setup.py bdist_wheel"
Set-Location "../"
