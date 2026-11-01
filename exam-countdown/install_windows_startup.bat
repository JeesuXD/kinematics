@echo off
rem Starts the Exam Countdown widget now and every time you log in to Windows.
rem Needs Python from python.org (tick "Add python.exe to PATH" while installing).

set "TARGET=%~dp0exam_countdown.pyw"

where pythonw >nul 2>nul
if errorlevel 1 (
  echo Python was not found. Install it from https://www.python.org/downloads/
  echo and tick "Add python.exe to PATH" during setup, then run this again.
  pause
  exit /b 1
)

for /f "delims=" %%P in ('where pythonw') do (
  set "PYW=%%P"
  goto :found
)
:found

powershell -NoProfile -Command ^
  "$s = (New-Object -ComObject WScript.Shell).CreateShortcut([Environment]::GetFolderPath('Startup') + '\Exam Countdown.lnk');" ^
  "$s.TargetPath = '%PYW%';" ^
  "$s.Arguments = '\"%TARGET%\"';" ^
  "$s.WorkingDirectory = '%~dp0';" ^
  "$s.Save()"

start "" "%PYW%" "%TARGET%"
echo.
echo Done! The widget is on your desktop and will start automatically when you log in.
echo To remove it from startup: press Win+R, type shell:startup, delete "Exam Countdown".
pause
