# Get the path of the script directory, no matter where it's executed from.
$scriptDirPath = Split-Path $script:MyInvocation.MyCommand.Path

# Save current working directory, we'll need to change back to this directory later to cleanup
$workDir = (Get-Location).Path

# Calculate path to the module source directory
$setupDirPath = Join-Path $scriptDirPath "Source"

# Switch working directories, invoke Python and setup develop mode, clean up
Set-Location $setupDirPath
Invoke-Expression "python.exe setup.py develop"
Set-Location $workDir