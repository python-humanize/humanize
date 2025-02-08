# This script is used by the Github Action to install gettext on the CI

nuget install Gettext.Tools -OutputDirectory c:\nuget

$gettextPath = (
    Get-ChildItem -Path "C:\nuget" -Directory -Filter "Gettext.Tools.*" |
    Select-Object -First 1
).FullName

Add-Content $env:GITHUB_PATH "$gettextPath\tools\bin"
