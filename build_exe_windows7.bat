py -3.8 -m PyInstaller ^
  --onefile ^
  --name WordMaze ^
  --collect-all PyQt5 ^
  --collect-submodules src ^
  --hidden-import src.main ^
  --add-data "data;data" ^
  --add-data "assets;assets" ^
  run_wordmaze.py
