from constants import BEACH, DESERT, FOREST, GRASSLAND, HEIGHT, JUNGLE, MOUNTAIN, OCEAN, SAVE_LOCATION, SNOW, WIDTH, UNOCUPPIED

def scan(world, target, delete=False):
    reslist = []
    for y in range(HEIGHT):
        for x in range(WIDTH):
            if world[y][x] == target:
                if not delete:
                    reslist.append([x, y])
                else:
                    world[y][x] = UNOCUPPIED
    return reslist

def messy_noise(val, noise_set):
    return noise_set[0](val)+0.5*noise_set[1](val)+0.25*noise_set[2](val)

def clamp(val, nmin=0, nmax=1):
    return max(nmin, min(val, nmax))

def log(*args,end='\n'):
    with open(SAVE_LOCATION, 'a') as w:
        w.write(' '.join([str(arg) for arg in args])+end)

def colour(char):
    if char == GRASSLAND or char == FOREST:
        return 'green'
    elif char == OCEAN:
        return 'blue'
    elif char == MOUNTAIN:
        return 'magenta'
    elif char == JUNGLE:
        return 'cyan'
    elif char == SNOW:
        return 'white'
    elif char == DESERT or char == BEACH:
        return 'yellow'
    else:
        return 'white'
