# Civsim v1.0 by Utilityhotbar

import pprint
from perlin_noise import PerlinNoise
import random
import rpgtools
import os
import time
import math
import termcolor
import copy

SAVE_LOCATION = 'logfile.txt'

pp = pprint.PrettyPrinter()
tnoise = [PerlinNoise(octaves=2, seed=random.randint(1,10000)), PerlinNoise(octaves=4, seed=random.randint(1,10000)), PerlinNoise(octaves=88, seed=random.randint(1,10000))]
enoise = [PerlinNoise(octaves=4, seed=random.randint(1,10000)), PerlinNoise(octaves=10, seed=random.randint(1,10000)), PerlinNoise(octaves=20, seed=random.randint(1,10000))]


def messy_noise(val, noise_set):
    return noise_set[0](val)+0.5*noise_set[1](val)+0.25*noise_set[2](val)


def clamp(val, min=0, max=1):
    if val < min:
        return min
    elif val > max:
        return max
    else:
        return val


def log(*args,end='\n'):
    with open(SAVE_LOCATION, 'a') as w:
        w.write(' '.join([str(arg) for arg in args])+end)


HEIGHT = 20
WIDTH = 50
AGE = 500  # In years
TEMP = [[messy_noise([i / WIDTH, j / HEIGHT], tnoise)+0.1 for i in range(WIDTH)] for j in range(HEIGHT)]
ELEV = [[messy_noise([i / WIDTH, j / HEIGHT], enoise) for i in range(WIDTH)] for j in range(HEIGHT)]
WORLD = [['?' for i in range(WIDTH)] for j in range(HEIGHT)]
CIV = [['' for i in range(WIDTH)] for j in range(HEIGHT)]
CIVLETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()-_=+[{]}\|;:,<.>/?'
CURR_CIV = 0
CIVLIST = []
YEAR = 0


class Civilisation:
    def __init__(self, name, symbol, origin, ancestor=None):
        self.name = name
        self.instability = -10
        self.symbol = symbol
        self.territory = [origin]
        self.home_biome = WORLD[origin[1]][origin[0]]
        self.power = rpgtools.roll('3d10')
        self.powerbase = 1
        self.techlevel = 0
        self.dead = False
        self.priorities = []
        self.age = 0
        for item in ['Expansion', 'Development', 'Growth', 'Stabilise']:  # Civilisation priorities determined randomly
            for _ in range(random.randint(1, 8)):
                self.priorities.append(item)

    def expand(self):
        if self.dead or self.territory == []:
            return
        for n in range(random.randint(2, 5)):
            attempt = random.choice(self.territory)
            rng = 1
            ax = random.randint(clamp(attempt[0]-rng, max=WIDTH-1), clamp(attempt[0]+rng, max=WIDTH-1))
            ay = random.randint(clamp(attempt[1]-rng, max=HEIGHT-1), clamp(attempt[1]+rng, max=HEIGHT-1))
            attempt_loc = WORLD[ay][ax]
            if not (attempt_loc == '~' or attempt_loc == self.symbol):  # Cannot expand into water
                c = 10 + max(50, 5*self.techlevel)  # Base 10% success chance, max +50% from technology
                if attempt_loc == self.home_biome:  # Bonus chance for expansion if attempting to expand into base biome
                    c += 20
                if CIV[ay][ax] != '':  # Spreading into occupied squares is harder
                    c -= 9
                if WORLD[ay][ax] == 'm':  # Mountains make it hard to spread
                    c -= 5
                elif WORLD[ay][ax] == 'g':  # grasslands easy to spread
                    c += 5
                roll = rpgtools.roll('1d100')
                if roll < c:
                    CIV[ay][ax] = self.symbol
                    self.territory.append([ax, ay])

    def update(self):
        self.age += 1
        self.territory = scan(CIV, self.symbol)
        if self.territory == []:
            self.dissolve()
        self.powerbase = len(self.territory)  # For each unit of land you hold you gain extra power
        self.power += self.powerbase*(0.8+(rpgtools.roll('6d10-6d10')/100))+self.powerbase*self.techlevel*3  # National fortune = Fortune (normal distribution) + tech
        self.instability += random.randint(1, math.ceil(self.powerbase/10)+1) - rpgtools.roll('3d6-3d6')
        if rpgtools.roll('2d100')<self.instability:
            if rpgtools.roll('1d6') == 1:
                self.dissolve()
            else:
                if rpgtools.roll('1d6') < 4:
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
        scan(CIV, self.symbol, delete=True)
        if self.territory:
            for _ in range(random.randint(1, math.ceil(self.powerbase/10)+1)):
                newseed = random.choice(self.territory)
                make_civ(newseed[0], newseed[1])

    def collapse(self, decimate=False):
        global CIVLETTERS
        log(f'{self.name} is collapsing.')
        self.instability += rpgtools.roll(f'{math.ceil(self.powerbase/10)}d6')
        self.power /= random.randint(2, 4)
        seeding_targets = []
        for x in range(random.randint(math.floor(len(self.territory)/1.5), len(self.territory))):
            rmtarget = random.choice(self.territory)
            seeding_targets.append(rmtarget)
            self.territory.remove(rmtarget)
            CIV[rmtarget[1]][rmtarget[0]] = ''
        if not decimate and seeding_targets:  # Natural disasters do not create new states
            for _ in range(random.randint(1, math.ceil(self.powerbase / 10) + 1)):
                newseed = random.choice(seeding_targets)
                seeding_targets.remove(newseed)
                make_civ(newseed[0], newseed[1], parent=self, expand=True)
                if not seeding_targets:
                    return

    def execute(self):
        bank = 0
        baseactions = math.ceil(self.powerbase/10+1)
        maxactions = math.ceil(self.powerbase/5+1)
        for _ in range(random.randint(baseactions,maxactions)):
            curr_option = random.choice(self.priorities)
            if curr_option == 'Expansion':
                log(f'{self.name} is expanding')
                if self.power > 10:
                    self.power -= 10
                    self.expand()
                else:
                    log(f'{self.name} failed to expand')
            elif curr_option == 'Development':
                log(f'{self.name} is developing')
                if self.power > 20:
                    self.power -= 20
                    self.techlevel += rpgtools.roll('1d10')/10
                else:
                    log(f'{self.name} failed to develop')
            elif curr_option == 'Growth':
                log(f'{self.name} is growing')
                bank += self.power * (rpgtools.roll('1d4')/10)
            elif curr_option == 'Stabilise':
                log(f'{self.name} is stabilising')
                self.instability *= random.random()
        self.power += bank

def generate(world, tmap, emap):
    for y in range(HEIGHT):
        for x in range(WIDTH):
            local_t = tmap[y][x]
            local_e = emap[y][x]
            if local_e < 0.001:  # If too low, ocean by default
                world[y][x] = '~'  # Ocean
            elif local_e < 0.100:  # Next to oceans are beaches
                world[y][x] = 'b'  # Beach
            elif local_e > 0.4:  # If too tall, mountain by default
                world[y][x] = 'm'
            else:  # if in temperate region, determine biome based on climate
                if local_t < -0.2:  # snow
                    world[y][x] = 's'
                elif local_t < 0:  # tundra
                    world[y][x] = 't'
                elif local_t < 0.1:  # grassland
                    world[y][x] = 'g'
                elif local_t < 0.2:  # forest
                    world[y][x] = 'f'
                elif local_t < 0.3:
                    world[y][x] = 'j'  # jungle
                else:
                    world[y][x] = 'd'  # desert
    return world


def seed(world, num_attempts=10):
    global CURR_CIV
    for i in range(num_attempts):
        tx = random.randint(0, WIDTH-1)
        ty = random.randint(0, HEIGHT-1)
        target = world[ty][tx]
        if target != '~':
            make_civ(tx, ty)


def make_civ(x, y, parent=None, expand=True):
    global CURR_CIV
    if CURR_CIV > len(CIVLETTERS)-1:
        return
    CIV[y][x] = CIVLETTERS[CURR_CIV]
    nc = Civilisation('Civ {}+{}'.format(CIVLETTERS[CURR_CIV], CURR_CIV), CIVLETTERS[CURR_CIV], [x, y], ancestor=parent)
    CIVLIST.append(nc)
    CURR_CIV += 1
    if expand==True:
        nc.expand()


def scan(world, target, delete=False):
    reslist = []
    for y in range(HEIGHT):
        for x in range(WIDTH):
            if world[y][x] == target:
                if not delete:
                    reslist.append([x, y])
                else:
                    world[y][x] = ''
    return reslist


def colour(char):
    if char == 'g' or char == 'f':
        return 'green'
    elif char == '~':
        return 'blue'
    elif char == 'm':
        return 'magenta'
    elif char == 'j':
        return 'cyan'
    elif char == 's':
        return 'white'
    elif char == 'd' or char == 'b':
        return 'yellow'
    else:
        return 'white'


def display(world, year=None):
    os.system('cls')
    print(f'Year {year}')
    for y in range(HEIGHT):
        for x in range(WIDTH):
            if CIV[y][x]:
                print(termcolor.colored(CIV[y][x], 'red'), end='')
            else:
                # print(' ', end='')
                print(termcolor.colored(world[y][x], colour(world[y][x])), end='')
        print('')


def update(WORLD):
    for cand in CIVLIST:
        cand.execute()
        cand.update()


def main():
    global YEAR
    generate(WORLD, TEMP, ELEV)
    seed(WORLD)
    while YEAR < AGE:
        display(WORLD, YEAR)
        update(WORLD)
        if random.randint(1, 20) == 20:
            seed(WORLD, rpgtools.roll('1d6'))
        YEAR += 1
        time.sleep(0.1)


if __name__ == '__main__':
    main()
