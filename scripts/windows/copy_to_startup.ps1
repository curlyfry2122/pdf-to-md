# Copy VBS file to Windows Startup folder
$sourceFile = "start_auto_converter_silent.vbs"
$startupFolder = [Environment]::GetFolderPath('Startup')
$destFile = Join-Path $startupFolder "start_auto_converter_silent.vbs"

Write-Host "Copying file to Startup folder..."
Write-Host "Source: $sourceFile"
Write-Host "Destination: $destFile"

Copy-Item $sourceFile $destFile -Force

if (Test-Path $destFile) {
    Write-Host "`nSUCCESS! File copied to Startup folder."
    Write-Host "The auto converter will start automatically on next login."
} else {
    Write-Host "`nERROR: File was not copied successfully."
}
