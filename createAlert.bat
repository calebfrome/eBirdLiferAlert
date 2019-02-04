:: Wrapper batch file to run createAlert.py ::

::@echo OFF

:: Location of createAlert.py (if not set, current directory used)
set scriptPath=C:/Users/Caleb/Documents/Python/eBirdLiferAlert

:: Run python script ::
cd %scriptPath%
python createAlert.py
::cmd \k