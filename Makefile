#MIT LICENSE © Copyright 2021 KrazyKirby99999

WIN_PYTHON = python.exe
WIN_VENV = env\Scripts\${WIN_PYTHON}

LINUX_PYTHON = python3
LINUX_VENV = env/bin/${LINUX_PYTHON}

.DEFAULT_GOAL = help
.PHONY: help setup-dev-win python-run-win clean-win clean-linux python-run setup-dev-ubuntu setup-dev-arch

help:
	@echo ---------------HELP-----------------
	@echo -Generic
	@echo make help - display this message
	@echo -Windows
	@echo make setup-dev-win - setup the project for development, specifically for windows
	@echo make python-run-win - run the project using python, specifically for windows
	@echo make clean-win - clean the project of unneeded files, specifically for windows	
	@echo -LINUX
	@echo make clean-linux - clean the project of unneeded files, specifically for linux
	@echo make python-run - run the project using python, specifically for linux
	@echo -UBUNTU
	@echo make setup-dev-ubuntu - setup the project for development, specifically for ubuntu
	@echo -ARCH
	@echo make setup-dev-arch - setup the project for development, specifically for arch
	@echo ------------------------------------

setup-dev-win: clean-win
	@echo -----------SETUP-DEV-WIN-----------
	@echo Confirm that Python3 is installed? (Can be installed from https://www.python.org/ if needed)
	pause
	${WIN_PYTHON} -m pip install --upgrade pip
	${WIN_PYTHON} -m pip install virtualenv
	${WIN_PYTHON} -m venv env
	${WIN_VENV} -m pip install -r requirements.txt

python-run-win:
	@echo -----------PYTHON-RUN-WIN-----------
	${WIN_VENV} main.py

clean-win:
	@echo --------------CLEAN-WIN-------------
	IF EXIST *.pyc del /S *.pyc
	IF EXIST *.pyo del /S *.pyo
	IF EXIST build RMDIR /S /Q build
	IF EXIST dist RMDIR /S /Q dist
	IF EXIST *.egg-info del /S *.egg-info
	IF EXIST *.build RMDIR /S /Q *.build
	IF EXIST *.dist RMDIR /S /Q *.dist
	IF EXIST __pycache__ RMDIR /S /Q __pycache__

setup-dev-ubuntu: clean-linux
	@echo ----------SETUP-DEV-UBUNTU----------
	sudo apt install build-essential python3-dev python3-pip python3-venv
	${LINUX_PYTHON} -m venv env
	${LINUX_VENV} -m pip install --upgrade pip
	${LINUX_VENV} -m pip install -r requirements.txt

setup-dev-arch: clean-linux
	@echo -----------SETUP-DEV-ARCH-----------
	sudo pacman -S --noconfirm base-devel 
	${LINUX_PYTHON} -m venv env
	${LINUX_VENV} -m pip install --upgrade pip
	${LINUX_VENV} -m pip install -r requirements.txt

clean-linux:
	@echo -------------CLEAN-LINUX------------
	rm --force --recursive *.pyc
	rm --force --recursive *.pyo
	rm --force --recursive build/
	rm --force --recursive dist/
	rm --force --recursive *.egg-info
	rm --force --recursive *.build/
	rm --force --recursive *.dist/
	rm --force --recursive __pycache__

python-run:
	@echo -------------PYTHON-RUN-------------
	${LINUX_VENV} main.py
