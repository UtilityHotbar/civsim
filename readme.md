# Civsim
## Introduction
Civsim is a basic civilisation simulation and modelling system built in Python 3.8. It requires the following dependencies:

Python:
```
perlin_noise==1.7
termcolor==1.1.0
```
Other:
```
Python3
Git
Make
```

## Usage
Download
```
git clone https://github.com/UtilityHotbar/civsim.git
```
Setup (create virtual environment and install dependencies)
```
cd civsim
```
```
#Windows (7, 8, 10)
make setup-dev-win

#Debian (Debian, Ubuntu, Pop!_OS, etc.)
make setup-dev-ubuntu

#Arch (Arch, Manjaro, EndeavorOS, etc.)
make setup-dev-arch
```
Run
```
#Windows (7, 8, 10)
make python-run-win
```
```
#Linux (Debian, Ubuntu, Pop!_OS, Arch, Manjaro, EndeavorOS, etc.)
make python-run
```

## Features
Currently civsim supports the following features:
* Terrain generation using Perlin noise (including biomes)
* Civilisation generation with different priorities and favoured terrain etc
* Civilisation growth, expansion, stabilisation, destabilisation, collapse, and death
* Successor states and breakaway states

## Todo
* Diplomacy between nations
* Possibly some sort of ruler system to see national priorities change over time
* Playing as a civ?
* Expanding over water (Independent agents?)

![Demo image](https://github.com/UtilityHotbar/civsim/blob/master/civsim.png)