' PDF Auto Converter - Silent Launcher
' This VBScript runs the batch file without showing a console window
' Place this file in your Windows Startup folder for automatic startup

Dim objShell, strBatchPath, strWorkingDir

' Set the working directory to the project folder
strWorkingDir = "c:\Users\jdevine\dev\pdf-to-md"

' Path to the batch file
strBatchPath = strWorkingDir & "\start_auto_converter.bat"

' Create shell object
Set objShell = CreateObject("WScript.Shell")

' Run the batch file hidden (0 = hidden window, False = don't wait)
objShell.Run """" & strBatchPath & """", 0, False

Set objShell = Nothing
