@echo off
CALL conda.bat activate civitai
python run.py --l 1 --r 13428 --save_dir "1-13428"
@echo on
pause