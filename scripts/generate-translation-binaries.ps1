Get-ChildItem -Path "src\humanize\locale" -Directory | ForEach-Object {
    $locale = $_.Name
    Write-Host "$locale"
    # compile to binary .mo
    msgfmt --check -o "src\humanize\locale\$locale\LC_MESSAGES\humanize.mo" "src\humanize\locale\$locale\LC_MESSAGES\humanize.po"
}
