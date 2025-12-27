@echo off
cd /d "%~dp0"

py -3.10 -m pip install --quiet pyinstaller

py -3.10 -m PyInstaller ^
  --onefile ^
  --name WordMaze ^
  --collect-submodules src ^
  --hidden-import src.main ^
  --add-data "data;data" ^
  --add-data "assets;assets" ^
  run_wordmaze.py

pause
