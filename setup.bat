@echo off
CALL conda.bat env create -f environment.yml
CALL conda.bat activate civitai
pip install cloudscraper
pip install click
@echo on
pause