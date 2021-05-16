from perlin_noise import PerlinNoise
from random import randint

from civsim.civ.constants import UNOCCUPIED
from civsim.world.constants import BEACH, DESERT, FOREST, GRASSLAND, JUNGLE, MOUNTAIN, OCEAN, SEA_LEVEL, SNOW, TUNDRA
from civsim.world.utils import messy_noise


class World:
    """
    A class to build a world.

    """
    tnoise = [
        PerlinNoise(octaves=2, seed=randint(1,10000)),
        PerlinNoise(octaves=4, seed=randint(1,10000)),
        PerlinNoise(octaves=88, seed=randint(1,10000))
    ]
    enoise = [
        PerlinNoise(octaves=4, seed=randint(1,10000)),
        PerlinNoise(octaves=10, seed=randint(1,10000)),
        PerlinNoise(octaves=20, seed=randint(1,10000))
    ]

    def __init__(self, height, width):
        """
        Initialize world parameters.

        """
        self._name = 'Terra' # TODO random planet name generator
        self._symbol = '🜨' # TODO random symbol generator
        self._height = height
        self._width = width
        self._emap = None
        self._tmap = None
        self._wgrid = None
        self._cgrid = None
        self._year = 0
    
    def __str__(self):
        """
        Ostende te!
        
        """
        return f'{self._name} {self._symbol}'

    def genesis(self):
        """
        In the beginning Python created the heavens and the earth.
        
        Generate world structure, temperature map, elevation map and fill world with biomes.
        
        """
        self._wgrid = [[OCEAN]*self._width for _ in range(self._height)]
        self._cgrid = [[UNOCCUPIED]*self._width for _ in range(self._height)]

        self._emap = [[messy_noise([i / self._width, j / self._height], type(self).enoise)
         for i in range(self._width)] for j in range(self._height)]
        self._tmap = [[messy_noise([i / self._width, j / self._height], type(self).tnoise)+0.1
         for i in range(self._width)] for j in range(self._height)]

        self._fill_with_biomes()

    def _fill_with_biomes(self):
        """
        Let the water under the sky be gathered to one place, and let dry ground appear.
        
        """
        for lat in range(self._height):
            for long in range(self._width):
                local_t = self._tmap[lat][long]
                local_e = self._emap[lat][long]
                if local_e >= SEA_LEVEL and local_e < 0.100:  # next to oceans are beaches
                    self._wgrid[lat][long] = BEACH
                elif local_e > 0.4:  # if too tall, mountain by default
                    self._wgrid[lat][long] = MOUNTAIN
                elif local_e > SEA_LEVEL:  # if in a temperate region, determine biome based on climate
                    if local_t < -0.2:
                        self._wgrid[lat][long] = SNOW
                    elif local_t < 0:
                        self._wgrid[lat][long] = TUNDRA
                    elif local_t < 0.1:
                        self._wgrid[lat][long] = GRASSLAND
                    elif local_t < 0.2:
                        self._wgrid[lat][long] = FOREST
                    elif local_t < 0.3:
                        self._wgrid[lat][long] = JUNGLE
                    else:
                        self._wgrid[lat][long] = DESERT
    
    @property
    def wgrid(self):
        return self._wgrid

    @property
    def cgrid(self):
        return self._cgrid

    @property
    def height(self):
        return self._height

    @property
    def width(self):
        return self._width

    @property
    def year(self):
        return self._year

    @property
    def name(self):
        return self._name

    @property
    def symbol(self):
        return self._symbol
    
    def inc_year(self):
        self._year +=1
