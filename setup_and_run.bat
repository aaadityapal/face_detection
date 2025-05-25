@echo off
echo Face Detection Application Setup
echo ==============================

echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Setup complete!
echo.
echo Choose which version to run:
echo 1. Command Line Version
echo 2. GUI Version
echo 3. Exit

choice /C 123 /N /M "Enter your choice (1-3): "

if errorlevel 3 goto exit
if errorlevel 2 goto gui
if errorlevel 1 goto cli

:cli
echo.
echo Starting Command Line Version...
python face_detection_app.py
goto exit

:gui
echo.
echo Starting GUI Version...
python face_detection_gui.py
goto exit

:exit
echo.
echo Exiting...
pause 