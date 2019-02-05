:: Setup script ::

::@echo OFF

:: Location of xlrd
set scriptPath=C:/Users/Caleb/Documents/Python/eBirdLiferAlert/xlrd-1.2.0

:: Tell python about xlrd ::
cd %scriptPath%
python setup.py install

echo "Setup complete"

cmd \k