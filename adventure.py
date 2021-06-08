import rpgtools.coretools
import rpgtools.mini_dungeon
import rpgtools.dungeon
import civsim
import random
import textui
import blessed
import pickle
import utils

# TODO: Each layer of the dungeon is one layer back in time???
# TODO: Dynamically generate dungeon as player moves through it. (AI runs DFS)


def generate_system():
    mode = rpgtools.coretools.generate_menu([
        'Create star system manually',
        'Create star system randomly',
        'Create star system with default planets'])
    star_system = []
    # World generation
    worldnum = utils.input_number('Enter number of worlds in star system: ')
    for i in range(worldnum):
        worldname = input(f'Enter world name (default "World {i}"): ')
        if mode == 0:
            worldwidth = utils.input_number('Enter world width (default 50): ', default_answer=50)
            worldheight = utils.input_number('Enter world height (default 50): ', default_answer=20)
            worldtmod = utils.input_number('Enter world temperature mod (-0.3 - 0.3, default 0.1): ', default_answer=0.1, use_float=True)
            worldemod = utils.input_number('Enter world elevation mod (-0.3 - 0.3, default 0) : ', default_answer=0, use_float=True)
        elif mode == 1:
            worldwidth = random.randint(30, 70)
            worldheight = random.randint(30, 70)
            worldtmod = (random.random()*4)-2
            worldemod = (random.random() * 4) - 2
        else:
            worldwidth = 50
            worldheight = 20
            worldtmod = 0.1
            worldemod = 0
        if not worldname:
            worldname = f"World {i}"
        planet = civsim.Planet(worldname,
                               worldwidth,
                               worldheight,
                               temp_mod=worldtmod,
                               elev_mod=worldemod)
        planet.generate()
        star_system.append(planet)
    age = utils.input_number('Enter age of system: ')
    for _ in range(age):
        [world.update() for world in star_system]
    return star_system


class OverworldGM(rpgtools.mini_dungeon.GM):
    def __init__(self, gmfile):
        super().__init__(gmfile)
        self.starsystem = []
        self.party = []
        self.mode = 'overworld'
        self.current_world = None
        self.current_dungeon = None
        self.current_dungeon_layer = 0
        self.current_dungeon_room = None
        self.time_elapsed = 0
        self.term = blessed.Terminal()
        self.y_offset = 2  # Counter the mysterious negative y offset that seems to exist???
        self.location = []

    def run_campaign(self, starsystem, party, start_world=0, start_coords=None):
        self.starsystem = starsystem
        self.party = party
        local_world = self.starsystem[start_world]
        if not start_coords:
            for rx in range(local_world.w):
                for ry in range(local_world.h):
                    if local_world.world[ry][rx] != '~':
                        break
        else:
            rx, ry = start_coords
        super().gm_print(f'Starting campaign on {local_world.name}')
        self.current_world = local_world
        self.campaign_loop(rx, ry)

    def update_frame(self):
        if self.mode == 'overworld':
            print(self.term.home + self.term.move_down(self.y_offset) + self.term.move_right(70), 'MINIMAP PARTY               ')
            minimap = textui.Frame(self.term, 70, 1 + self.y_offset, 7, 7, frame='.')
            minimap.push(self.getmapdata(self.location[0], self.location[1]))
            minimap.display(dynamic_height=False, centered=True)
            party = textui.Frame(self.term, 78, 1 + self.y_offset, 20, 7, frame='.')
            for person in self.party:
                party.push(f'{person.name[:min(len(person.name), 10)]}'+' '*(9-len(person.name))+f'   {person.data["HP"]} HP')
            party.display(dynamic_height=False)
            print(self.term.home + self.term.move_down(self.term.height - 1))
        elif self.mode == 'dungeon':
            print(self.term.home + self.term.move_down(self.y_offset) + self.term.move_right(70), 'MINIMAP                     ')
            minimap = textui.Frame(self.term, 70, 1 + self.y_offset, 17, 17, frame='.')
            minimap.push(self.current_dungeon.display_map(
                self.current_dungeon_layer,
                self.curr_dungeon_room.x,
                self.curr_dungeon_room.y, display=False).replace('?', ' '))
            minimap.display()
            print(self.term.home + self.term.move_down(self.term.height - 1))

    def gm_print(self, *args):
        self.update_frame()
        super().gm_print('\n'.join(self.term.wrap(' '.join(args), 65)))

    def campaign_loop(self, sx, sy):
        self.location = [sx, sy]
        with self.term.fullscreen():
            done = False
            while not done:
                curr_location = self.current_world.world[self.location[0]][self.location[1]]
                self.gm_print(f'You are currently standing on: {curr_location}')
                potential_ruins = self.current_world.ruins[self.location[0]][self.location[1]]
                if len(potential_ruins) > 3:
                    self.gm_print('There are ruins here.')
                cmdchain = [_.strip() for _ in input(f'({self.party[0].name}) ').lower().split('.')]
                if cmdchain == ['']:
                    continue
                for i in cmdchain:
                    words = i.split()
                    cmd = words[0]
                    if cmd == 'quit' or cmd == 'q':
                        self.gm_print(self.data.table_fetch('SessionEndText'))
                        done = True
                    elif cmd == 'go' or cmd == 'g':
                        if words[1] == 'north' or words[1] == 'n':
                            self.location[1] -= 1
                            if self.location[1] < 0:
                                self.location[1] = 0
                                self.gm_print(self.data.table_fetch('WorldEdgeText'))
                        elif words[1] == 'south' or words[1] == 's':
                            self.location[1] += 1
                            if self.location[1] > self.current_world.h-1:
                                self.location[1] = self.current_world.h
                                self.gm_print(self.data.table_fetch('WorldEdgeText'))
                        elif words[1] == 'west' or words[1] == 'w':
                            self.location[0] -= 1
                            if self.location[0] < 0:
                                self.location[0] = 0
                                self.gm_print(self.data.table_fetch('WorldEdgeText'))
                        elif words[1] == 'east' or words[1] == 'e':
                            self.location[0] += 1
                            if self.location[0] > self.current_world.w - 1:
                                self.location[0] = self.current_world.w
                                self.gm_print(self.data.table_fetch('WorldEdgeText'))
                    elif cmd == 'explore' or cmd == 'e':
                        self.gm_print('You explore.')
                    elif cmd == 'delve' or cmd == 'd':
                        self.explore_dungeon()
                        if len(potential_ruins) > 3:
                            self.gm_print('You enter the ruins...')
                        else:
                            self.gm_print('Nothing to delve into.')
                    elif cmd == 'world' or cmd == 'w':
                        civsim.display(self.current_world, self.term, highlight=self.location)
                        input('(Press ENTER to exit world map)')
                        utils.screen_clear()
                    elif cmd == 'help' or cmd == 'h':
                        self.gm_print('Commands available:\n'
                                      '(H)ELP - Display help text\n'
                                      '(G)O N/S/E/W - Move in that direction\n'
                                      '(Q)UIT - Exit game\n'
                                      '(E)XPLORE - Explore location\n'
                                      '(D)ELVE - Enter dungeon\n'
                                      '(W)ORLD - Display world map')
                    else:
                        self.gm_print('Command not found.')

    def getmapdata(self, x, y):
        topleft_x = max(x-2, 0)
        topleft_y = max(y-2, 0)
        botrght_x = min(x+2, self.current_world.w-1)
        botrght_y = min(y+2, self.current_world.h-1)
        localmap = ''
        for ty in range(topleft_y, botrght_y+1):
            for tx in range(topleft_x, botrght_x+1):
                if (ty, tx) == (y, x):
                    localmap += '@'
                else:
                    localmap += self.current_world.world[ty][tx]
            localmap += '\n'
        return localmap

    def explore_dungeon(self):
        print(self.term.clear)
        self.mode = 'dungeon'
        self.current_dungeon = rpgtools.dungeon.Dungeon('testdungeon', 3, display=False)
        self.current_dungeon_layer = 0
        curr_dungeon_level = self.current_dungeon.directory[self.current_dungeon_layer]
        self.curr_dungeon_room = curr_dungeon_level[0]
        self.gm_print('You enter the dungeon...')
        while True:
            self.curr_dungeon_room.visited = True
            self.gm_print('You are currently standing in a room of type', self.curr_dungeon_room.kind)
            optlist = list(self.curr_dungeon_room.exits.keys())
            optlist.sort()
            if self.curr_dungeon_room.kind == '<':
                optlist.append('Go up')
            c = optlist[rpgtools.coretools.generate_menu(optlist, printfunc=self.gm_print)]
            if c == 'Go up':
                if self.curr_dungeon_room.entrance == 'EXIT':
                    self.gm_print('You leave the dungeon.')
                    break
            else:
                self.curr_dungeon_room = self.curr_dungeon_room.exits[c]
        print(self.term.clear)
        self.mode = 'overworld'



class OverworldPlayer(rpgtools.mini_dungeon.Player):
    def __init__(self, name):
        super().__init__(name)
        self.x = 0
        self.y = 0
        self.skills = {}


if __name__ == '__main__':
    try:
        with open('world_save.save', 'rb') as save:
            ld = input('Found pre-generated world, do you want to load? (y/n)> ').lower()
            if ld == 'y':
                myStarSystem = pickle.load(save)
            else:
                raise FileNotFoundError
    except FileNotFoundError:
        myStarSystem = generate_system()
        with open('world_save.save', 'wb') as save:
            pickle.dump(myStarSystem, save)
    # Character generation
    name = input('Enter your name: ')
    myPlayer = OverworldPlayer(name)
    gm = OverworldGM('gm.txt')
    gm.run_campaign(myStarSystem, [myPlayer])
