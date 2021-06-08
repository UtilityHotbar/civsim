from constants import BEACH, DESERT, FOREST, GRASSLAND, HEIGHT, JUNGLE, MOUNTAIN, OCEAN, SAVE_LOCATION, SNOW, WIDTH, UNOCCUPIED
import os
import platform

def scan(world, target, delete=False):
    reslist = []
    for y in range(HEIGHT):
        for x in range(WIDTH):
            if world[y][x] == target:
                if not delete:
                    reslist.append([y, x])
                else:
                    world[y][x] = UNOCCUPIED
    return reslist


def messy_noise(val, noise_set):
    return noise_set[0](val)+0.5*noise_set[1](val)+0.25*noise_set[2](val)


def clamp(val, nmin=0, nmax=1):
    return max(nmin, min(val, nmax))


def log(*args,end='\n'):
    with open(SAVE_LOCATION, 'a') as w:
        w.write(' '.join([str(arg) for arg in args])+end)


def colour(char, term):
    if char == GRASSLAND or char == FOREST:
        return term.green
    elif char == OCEAN:
        return term.blue
    elif char == MOUNTAIN:
        return term.magenta
    elif char == JUNGLE:
        return term.cyan
    elif char == SNOW:
        return term.white
    elif char == DESERT or char == BEACH:
        return term.yellow
    else:
        return term.white


def input_number(prompt='', default_answer=None, use_float=False):
    while True:
        n = input(prompt)
        try:
            if (n == '') and (default_answer != None):
                return default_answer
            if use_float:
                n = float(n)
            else:
                n = int(n)
        except ValueError:
            if (default_answer != None):
                print('Error - Please enter a number or an empty input for default.')
            else:
                print('Error - Please enter a number.')
            continue
        return n

def screen_clear():
    if platform.system() == 'Windows':
        os.system('cls')
    else:
        os.system('clear')
