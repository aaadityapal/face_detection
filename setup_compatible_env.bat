@echo off
echo Face Detection Application - Compatible Environment Setup
echo ======================================================

echo Checking if Python 3.10 is installed...
where python3.10 >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo Python 3.10 is already installed.
) else (
    echo Python 3.10 is not installed.
    echo Please download and install Python 3.10 from:
    echo https://www.python.org/downloads/release/python-31011/
    echo.
    echo After installation, run this script again.
    pause
    exit /b
)

echo.
echo Creating virtual environment...
if not exist "venv" (
    python3.10 -m venv venv
) else (
    echo Virtual environment already exists.
)

echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Installing dependencies...
pip install setuptools==68.2.2
pip install opencv-python==4.8.0.76 numpy==1.24.3 deepface==0.0.79 pillow==10.0.0

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
deactivate
pause 