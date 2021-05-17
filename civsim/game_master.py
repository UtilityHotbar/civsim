"""Main agent which controls gameloop, world and civ creation/interactions."""
import os
from platform import system
from random import randint
from time import sleep

from termcolor import colored

from civsim.civ.civ import Civilisation
from civsim.config import AGE
from civsim.third.rpgtools.main import roll
from civsim.utils import log
from civsim.world.constants import BIOME_COLOURS, OCEAN
from civsim.world.world import World

OS = system()


class GameMaster():
    """A class to rule them all."""

    world_compendium = {}
    civ_compendium = {}

    def __init__(self, mode, debug):
        """Initialize Eden project parameters."""
        self._cpu = bool(mode)
        self._debug = debug

    def creation(self, height=20, width=50, pioners=10):
        """You only have 7 days!."""
        world = World(height, width)
        world.genesis()
        type(self).world_compendium[world.name] = world
        self._adam(pioners, world)

    def _adam(self, pioners, world):
        """Early backers."""
        for _ in range(pioners):
            lat = randint(0, world.height-1)
            long = randint(0, world.width-1)
            biome_coord = world.wgrid[lat][long]
            if biome_coord != OCEAN:
                if not self._cpu:
                    Civilisation.born_civ(lat, long, world, cpu=self._cpu)
                    self._cpu = True
                else:
                    Civilisation.born_civ(lat, long, world)

    def hourglass(self):
        """Release the Sands."""
        # TODO rework for multiple worlds
        for _, world in type(self).world_compendium.items():
            while world.year < AGE:
                self.display()
                self._progress()
                if randint(1, 20) == 20:
                    self._adam(roll('1d6'), world)
                world.inc_year()
                sleep(0.1)

    def _progress(self):
        """Avanti."""
        # list is needed because items returns an iterator and we are updating the dictionary
        civs_this_turn = list(type(self).civ_compendium.items())
        for _, civ in civs_this_turn:
            if civ:
                civ.actions()
                civ.cadastre()
            else:
                log('GHOST CIV')

    def display(self):
        """Depending of the user system."""
        # TODO rework for multiple worlds
        if OS == 'Windows':
            os.system('cls')

        else:
            os.system('clear')

        for _, world in type(self).world_compendium.items():
            print(f'Year {world.year}')
            if self._debug:
                for _, civ in type(self).civ_compendium.items():
                    print(civ)

            for lat in range(world.height):
                for long in range(world.width):
                    biome = world.wgrid[lat][long]
                    civ = world.cgrid[lat][long]
                    if world.cgrid[lat][long]:
                        print(colored(civ, 'red'), end='')
                    else:
                        print(colored(biome, BIOME_COLOURS[biome]), end='')
                print('')
