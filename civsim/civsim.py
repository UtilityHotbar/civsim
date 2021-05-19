# Civsim v0.2 by UtilityHotbar

import math
import os
import platform
import random
import time

import termcolor
from perlin_noise import PerlinNoise

import rpgtools.lang_gen
import rpgtools.main
import rpgtools.table_process
from constants import *
from utils import *

OS = platform.system()

tnoise = [PerlinNoise(octaves=2, seed=random.randint(1, 10000)),
          PerlinNoise(octaves=4, seed=random.randint(1, 10000)),
          PerlinNoise(octaves=88, seed=random.randint(1, 10000))]
enoise = [PerlinNoise(octaves=4, seed=random.randint(1, 10000)),
          PerlinNoise(octaves=10, seed=random.randint(1, 10000)),
          PerlinNoise(octaves=20, seed=random.randint(1, 10000))]

TEMP = [[messy_noise([i / WIDTH, j / HEIGHT], tnoise) +
         0.1 for i in range(WIDTH)] for j in range(HEIGHT)]
ELEV = [[messy_noise([i / WIDTH, j / HEIGHT], enoise)
         for i in range(WIDTH)] for j in range(HEIGHT)]
WORLD = [[OCEAN]*WIDTH for _ in range(HEIGHT)]
CIV = [[UNOCCUPIED]*WIDTH for _ in range(HEIGHT)]
CURR_CIV = 0
CIVLIST = []
CIV_MISSIVES = []
YEAR = 0


class Civilisation:
    def __init__(self, name, symbol, origin, ancestor=None, control=False):
        self.language = rpgtools.lang_gen.make_language(
            'rpgtools/text/common_words.txt', rpgtools.table_process.Table('rpgtools/text/lang_struct.txt'))
        self.name = self.language.brute_force_translate(name)
        self.symbol = symbol
        self.territory = [origin]
        self.home_biome = WORLD[origin[0]][origin[1]]
        self.controlled_by_player = control
        # National stats
        self.instability = -10  # Low starting instability to ensure early expansion/survival
        self.power = rpgtools.main.roll('3d10')
        self.powerbase = 1
        self.techlevel = 0
        self.dead = False
        # Internal priorities
        self.priorities = [item for priority in CIV_PRIORITIES for item in (priority,) * randint(1, 8)]
        # Diplomatic profile
        self.profile = {
            'friendliness': rpgtools.main.roll('1d100'),
            'trustworthiness': rpgtools.main.roll('1d100'),
            'fearfulness': rpgtools.main.roll('1d100'),
            'reputation': 0
        }
        # Diplomatic relationships
        self.relationships = {}
        self.age = 0

    def expand(self):
        if self.dead or not self.territory:
            return

        for _ in range(random.randint(2, 5)):
            attempt = random.choice(self.territory)
            rng = 1
            ax = random.randint(
                clamp(attempt[1]-rng, nmax=WIDTH-1), clamp(attempt[1]+rng, nmax=WIDTH-1))
            ay = random.randint(
                clamp(attempt[0]-rng, nmax=HEIGHT-1), clamp(attempt[0]+rng, nmax=HEIGHT-1))
            attempt_loc = WORLD[ay][ax]

            # Cannot expand into water
            if not (attempt_loc == OCEAN or [ay, ax] in self.territory):
                # Base 10% success chance, max +50% from technology
                c = 10 + max(50, 5*self.techlevel)
                if attempt_loc == self.home_biome:  # Bonus chance for expansion if attempting to expand into base biome
                    c += 20
                if CIV[ay][ax] != UNOCCUPIED:  # Spreading into occupied squares is harder
                    c -= 5 + findciv(CIV[ay][ax]).techlevel
                if WORLD[ay][ax] == MOUNTAIN:  # Mountains make it hard to spread
                    c -= 5
                elif WORLD[ay][ax] == GRASSLAND:  # grasslands easy to spread
                    c += 5

                if rpgtools.main.roll('1d100') < c:
                    CIV[ay][ax] = self.symbol
                    self.territory.append([ay, ax])

    def update(self):
        self.age += 1
        if not self.territory:
            self.dissolve()
        # For each unit of land you hold you gain extra power
        self.powerbase = len(self.territory)
        # National fortune = Fortune (normal distribution) + tech
        self.power += self.powerbase * (0.8+(rpgtools.main.roll('6d10-6d10')/100)) + self.powerbase*self.techlevel*3
        self.instability += random.randint(1, math.ceil(self.powerbase/10)+1) - rpgtools.main.roll('3d6-3d6')
        if rpgtools.main.roll('2d100') < self.instability:
            if rpgtools.main.roll('1d6') == 1:
                self.dissolve()
            else:
                if rpgtools.main.roll('1d6') < 4:
                    self.collapse()
                else:
                    self.collapse(decimate=True)

    def dissolve(self):
        global CIVLETTERS
        log(f'{self.name} dissolved. It lasted {self.age} years and achieved a tech level of {self.techlevel}')
        self.dead = True
        if self in CIVLIST:
            CIVLIST.remove(self)
        CIVLETTERS += self.symbol
        if self.territory:
            scan(CIV, self.symbol, delete=True)
            n = range(random.randint(1, math.ceil(self.powerbase/10)+1))
            remnant = random.sample(self.territory, min(len(self.territory), n))
            for remnant in remnants:
                make_civ(remnant[0], remnant[1])

    def collapse(self, decimate=False):
        global CIVLETTERS
        log(f'{self.name} is collapsing.')
        self.instability += rpgtools.main.roll(
            f'{math.ceil(self.powerbase/10)}d6')
        self.power /= random.randint(2, 4)
        n = random.randint(math.floor(len(self.territory)/1.5), len(self.territory))
        lost_territory = random.sample(self.territory, min(len(self.territory), n))
        for area in lost_territory:
            self.territory.remove(area)
            CIV[area[0]][area[1]] = UNOCCUPIED
        if not decimate and lost_territory:  # Natural disasters do not create new states
            n = random.randint(1, math.ceil(self.base_power / 10) + 1)
            successor_states = random.sample(lost_territory, min(len(lost_territory), n))
            new_civs = []
            for successor_state in successor_states:
                new_civ = make_civ(successor_state[0], successor_state[1], parent=self)
                if new_civ:
                    new_civs.append(new_civ)
            for civ in new_civs:
                civ.expand()

    def execute(self):
        bank = 0
        baseactions = math.ceil(self.powerbase/10+1)
        maxactions = math.ceil(self.powerbase/5+1)
        curr_actions = random.randint(baseactions, maxactions)
        if self.controlled_by_player:
            print(f'YOU ARE CIV {self.name} ({self.symbol}).\n'
                  f'Power: {self.power:.2f} (Grow or expand to increase your power)\n'
                  f'Territory: {self.powerbase} (Expanding requires 10 power)\n'
                  f'Tech level: {self.techlevel:.2f} (Development requires 20 power)\n'
                  f'Instability: {self.instability:.2f} (Reducing instability is free)\n')
        for n in range(curr_actions):
            if self.controlled_by_player:
                print(f'YOU HAVE {curr_actions-n} ACTIONS REMAINING.')
                curr_option = CIV_PRIORITIES[rpgtools.main.generate_menu(CIV_PRIORITIES)]
            else:
                curr_option = random.choice(self.priorities)
            if curr_option == TERRITORIAL_EXPANSION:
                log(f'{self.name} is expanding')
                if self.power > 10:
                    self.power -= 10
                    self.expand()
                else:
                    log(f'{self.name} failed to expand')
            elif curr_option == TECH_DEVELOPMENT:
                log(f'{self.name} is developing')
                if self.power > 20:
                    self.power -= 20
                    self.techlevel += rpgtools.main.roll('1d10')/10
                else:
                    log(f'{self.name} failed to develop')
            elif curr_option == POPULATION_GROWTH:
                log(f'{self.name} is growing')
                bank += self.power * (rpgtools.main.roll('1d4')/10)
            elif curr_option == TERRITORIAL_STABILIZATION:
                log(f'{self.name} is stabilising')
                self.instability *= random.random()
        self.power += bank


def generate(world, tmap, emap):
    for y in range(HEIGHT):
        for x in range(WIDTH):
            local_t = tmap[y][x]
            local_e = emap[y][x]
            if local_e >= SEA_LEVEL and local_e < 0.100:  # next to oceans are beaches
                world[y][x] = BEACH
            elif local_e > 0.4:  # if too tall, mountain by default
                world[y][x] = MOUNTAIN
            elif local_e > SEA_LEVEL:  # if in a temperate region, determine biome based on climate
                if local_t < -0.2:
                    world[y][x] = SNOW
                elif local_t < 0:
                    world[y][x] = TUNDRA
                elif local_t < 0.1:
                    world[y][x] = GRASSLAND
                elif local_t < 0.2:
                    world[y][x] = FOREST
                elif local_t < 0.3:
                    world[y][x] = JUNGLE
                else:
                    world[y][x] = DESERT
    return world


def seed(world, num_attempts=10, player_control=False):
    global CURR_CIV
    pc = player_control
    for _ in range(num_attempts):
        tx = random.randint(0, WIDTH-1)
        ty = random.randint(0, HEIGHT-1)
        target = world[ty][tx]
        if target != OCEAN:
            make_civ(ty, tx, player_control=pc)
            # Player can only control 1 civ at a time
            if pc:
                pc = False


def make_civ(y, x, parent=None, expand=False, player_control=False):
    global CURR_CIV
    if CURR_CIV > len(CIVLETTERS)-1:
        return
    CIV[y][x] = CIVLETTERS[CURR_CIV]
    nc = Civilisation('Civ {}+{}'.format(CIVLETTERS[CURR_CIV], CURR_CIV), CIVLETTERS[CURR_CIV], [y, x],
                      ancestor=parent, control=player_control)
    CIVLIST.append(nc)
    CURR_CIV += 1
    if expand:
        nc.expand()
    return nc


def findciv(target):
    for civ in CIVLIST:
        if civ.symbol == target:
            return civ


def display(world, year=None):
    if OS == 'Windows':
        os.system('cls')
    else:
        os.system('clear')

    print(f'Year {year}')

    for y in range(HEIGHT):
        for x in range(WIDTH):
            if CIV[y][x]:
                print(termcolor.colored(CIV[y][x], 'red'), end='')
            else:
                print(termcolor.colored(world[y][x], colour(world[y][x])), end='')
        print('')


def update():
    for cand in CIVLIST:
        cand.execute()
        cand.update()


def main(mode):
    print(mode)
    if mode == 0:
        pc = True
    else:
        pc = False
    global YEAR
    generate(WORLD, TEMP, ELEV)
    seed(WORLD, player_control=pc)
    while YEAR < AGE:
        log(f'Year {YEAR}')
        display(WORLD, YEAR)
        update()
        if random.randint(1, 20) == 20:
            seed(WORLD, rpgtools.main.roll('1d6'))
        YEAR += 1
        time.sleep(0.1)


if __name__ == '__main__':
    print(MENU_LOGO)
    print(f'Civsim {VERSION} by UtilityHotbar')
    mode = rpgtools.main.generate_menu(['Realm Mode', 'Simulation Mode'])
    main(mode)