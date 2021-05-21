# Civsim
## Introduction
Civsim is a basic civilisation simulation and modelling system built in Python 3.8. It requires the following packages:

```
perlin_noise==1.7
termcolor==1.1.0
spacy==3.0.6
```

In order to use language features the `rpgtools` submodule should be installed. Run

`git submodule init`
and
`git submodule update`

To download the required submodules.

## Features
Currently civsim supports the following features:
* Terrain generation using Perlin noise (including biomes)
* Civilisation generation with different priorities and favoured terrain etc
* Civilisation growth, expansion, stabilisation, destabilisation, collapse, and death
* Successor states and breakaway states
* Playing as a civilisation (select Realm mode from the start menu)

## Todo
* Diplomacy between nations
* Possibly some sort of ruler system to see national priorities change over time
* Expanding over water (Independent agents?)

![Demo image](https://github.com/UtilityHotbar/civsim/blob/master/media/civsim.png)