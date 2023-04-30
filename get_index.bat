@echo off
CALL conda.bat activate civitai
python get_index.py --l 0 --r 1999 --save_dir "Civitai_Index/0-1999" --pool_size 16
@echo on
pause