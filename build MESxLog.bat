SET _version=1.1
SET _PATH_SOURCE=%CD%\
SET _WIN_=exe.win32-3.7

@echo.
@echo **************
@echo * COMPILANDO *
@echo **************
@echo.

"D:\Software\Python 3,7,4\python" "%_PATH_SOURCE%setup.py" build

@echo.
@echo *********************
@echo * COPIANDO ARCHIVOS *
@echo *********************
@echo.

Copy "%_PATH_SOURCE%Throbleshooting.txt" "%_PATH_SOURCE%build\%_WIN_%\"
Copy "%_PATH_SOURCE%vcruntime140.dll" "%_PATH_SOURCE%build\%_WIN_%\"
Copy "%_PATH_SOURCE%python3.dll" "%_PATH_SOURCE%build\%_WIN_%\"
Copy "%_PATH_SOURCE%MESxLog.bat" "%_PATH_SOURCE%build\%_WIN_%\"
Copy "%_PATH_SOURCE%ManualSetting.txt" "%_PATH_SOURCE%build\%_WIN_%\"
Copy "%_PATH_SOURCE%setting.cfg" "%_PATH_SOURCE%build\%_WIN_%\"
ren "%_PATH_SOURCE%build\%_WIN_%\setting.cfg" "setting_BKP.cfg"
ren "%_PATH_SOURCE%build\%_WIN_%\MESxLog.bat" "MESxLogs V%_Version%.bat"
ren "%_PATH_SOURCE%build\%_WIN_%" "MESxLog"
md "%_PATH_SOURCE%build\MESxLog\logs"

@echo.
@echo * Proceso Terminado *
@echo.
timeout /t 60
