@echo off
:: Use the py launcher to run the Python script
SET PYTHONW_EXE=py -3

:: Use a relative path for the script assuming the batch file is in the same directory as the script
SET SCRIPT_PATH=image_processor.py

:: Check if Python is available
%PYTHONW_EXE% --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Python is not available. Please ensure Python is installed and in your PATH.
    pause
    exit /b
)

:: Check if the Python script exists
IF NOT EXIST "%SCRIPT_PATH%" (
    echo Python script not found at %SCRIPT_PATH%
    echo Please ensure the script is in the current directory or correct the path.
    pause
    exit /b
)

:: Optional: Add context menu entry for image files. This step modifies the Windows registry.
:: WARNING: Modifying the registry can have unintended side effects. Proceed with caution.
echo This script can add a context menu entry for image files to process them with GPT-4 Vision.
echo Would you like to proceed with adding the context menu entry? (Y/N)
set /p CHOICE=Please enter your choice and press Enter:
if /i "%CHOICE%"=="Y" (
    reg add "HKCR\SystemFileAssociations\image\shell\ProcessImageWithGPT4" /ve /t REG_SZ /d "Process with GPT-4 Vision" /f
    reg add "HKCR\SystemFileAssociations\image\shell\ProcessImageWithGPT4\command" /ve /t REG_SZ /d "\"%PYTHONW_EXE%\" \"%SCRIPT_PATH%\" \"%%1\"" /f
    echo Context menu entry added successfully.
    echo Right-click on an image file and select "Process with GPT-4 Vision" to use the script.
) else (
    echo Context menu entry addition skipped.
)
pause