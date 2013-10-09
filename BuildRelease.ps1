param (
    [string]$format = "egg",
    [switch]$dev = $false
)

. ..\buildtools\build_func.ps1

Set-PythonPath @("..\buildtools")

Build-PythonModule "./Source" $format $dev

<#
    .SYNOPSIS
    Builds the arcpyext Python module.

    .DESCRIPTION
    The 'BuildRelease.ps1' PowerShell script provides a conveniant way to build the arcpyext Python module into a 
    distributable file. By default builds a release Python egg, but can optionally output any 'bdist' compatible 
    format (e.g. 'egg', 'wininst', 'tar', etc.), and can be made to make development builds (with a date string 
    appeneded to the version number).

    .PARAMETER format
    The 'bdist' compatible build format string (e.g. 'egg', 'wininst', 'sdist', 'tar', etc.)

    .PARAMETER dev
    Builds a 'development' package with a date/time stamp appended to the version number
    
    .EXAMPLE
    . ./BuildRelease.ps1
    Builds the module as a release-ready Python egg package.

    .EXAMPLE
    . ./BuildRelease.ps1 -format wininst
    Builds the module as the specified format, in this case, a Windows Installer.

    .EXAMPLE
    . ./BuildRelease.ps1 -format wininst -dev
    Builds the module with a date/time string appended to the build number, useful for continuous integration builds.
#>