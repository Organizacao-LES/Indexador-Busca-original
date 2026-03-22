@echo off
pip freeze > freeze_generated_requirements.txt

pip install -r freeze_generated_requirements.txt