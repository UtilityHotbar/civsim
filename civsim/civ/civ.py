from math import ceil, floor
from random import choice, randint, sample, random

#from civsim.third.rpgtools import lang_gen
from civsim.third.rpgtools.main import roll, generate_menu
#from civsim.third.rpgtools import table_process

from civsim.civ.utils import find_civ, sweep_the_land
from civsim.civ.constants import CIV_PRIORITIES, TECH_DEVELOPMENT, TERRITORIAL_EXPANSION, POPULATION_GROWTH, TERRITORIAL_STABILIZATION, UNOCCUPIED
from civsim.utils import clamp, log
from civsim.world.constants import DISASTERS, GRASSLAND, MOUNTAIN, OCEAN


class Civilisation:
    # TODO this class needs to be remade if multithread civs are added or multiplanets
    civ_ptr = 0
    civ_emblems = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()-_=+[{]}\|;:,<.>/?'

    def __init__(self, name, emblem, origin, world, ancestor=None, cpu=True):
        self._language = None#lang_gen.make_language('rpgtools/text/common_words.txt', table_process.Table('rpgtools/text/lang_struct.txt'))
        self._name = name#self.language.brute_force_translate(name)
        self._emblem = emblem
        self._world = world
        self._territory = [origin]
        self._home_biome = world.wgrid[origin[0]][origin[1]]
        self._age = 0
        self._dead = False
        self._cpu = cpu

        # Nation stats
        self._instability = -10  # Low starting instability to ensure early expansion/survival
        self._power = roll('3d10')
        self._powerbase = 1
        self._techlevel = 0

        # Internal priorities
        self._priorities = [item for priority in CIV_PRIORITIES for item in (priority,) * randint(1, 8)]

        # Diplomatic profile
        self._profile = {
            'friendliness': roll('1d100'),
            'trustworthiness': roll('1d100'),
            'fearfulness': roll('1d100'),
            'reputation': 0
        }

        # Diplomatic relationships
        self._relationships = {}

    def __str__(self):
        return f'{self._name} governs over {self._territory} with its homeland biome {self._home_biome}'
    
    @classmethod
    def born_civ(cls, lat, long, world, parent=None, expand=False, cpu=True):
        from civsim.game_master import GameMaster

        if cls.civ_ptr > len(cls.civ_emblems)-1:
            return
        world.cgrid[lat][long] = cls.civ_emblems[cls.civ_ptr]
        sprout = cls(f'{cls.civ_emblems[cls.civ_ptr]}+{cls.civ_ptr}', cls.civ_emblems[cls.civ_ptr], [lat, long], world, parent, cpu)
        if cpu:
            log(f'A new civilization {sprout.name} appeared at {[lat, long]}')
        else:
            log(f'A new civilization {sprout.name} appeared at {[lat, long]} controlled by the player')
        cls.civ_ptr +=1
        if expand:
            sprout._expand()
        GameMaster.civ_compendium[sprout.emblem] = sprout

        return sprout

    def actions(self):
        bank = 0
        baseactions = ceil(self._powerbase/10+1)
        maxactions = ceil(self._powerbase/5+1)
        curr_actions = randint(baseactions, maxactions)
        if not self._cpu:
            print(f'YOU ARE CIV {self._name}\n'
                  f'Power: {self._power} (Grow or expand to increase your power)\n'
                  f'Territory: {self._powerbase} (Expanding requires 10 power)\n'
                  f'Tech level: {self._techlevel} (Development requires 20 power)\n'
                  f'Instability: {self._instability} (Reducing instability is free)\n')
        for n in range(curr_actions):
            if not self._cpu:
                print(f'YOU HAVE {curr_actions-n} ACTIONS REMAINING')
                curr_option = CIV_PRIORITIES[generate_menu(CIV_PRIORITIES)]
            else:
                curr_option = choice(self._priorities)
            if curr_option == TERRITORIAL_EXPANSION:
                log(f'{self._name} is expanding')
                if self._power > 10:
                    self._power -= 10
                    self._expand()
                else:
                    log(f'{self._name} failed to expand')
            elif curr_option == TECH_DEVELOPMENT:
                log(f'{self._name} is developing')
                if self._power > 20:
                    self._power -= 20
                    self._techlevel += roll('1d10')/10
                else:
                    log(f'{self._name} failed to develop')
            elif curr_option == POPULATION_GROWTH:
                log(f'{self._name} is growing')
                bank += self._power * (roll('1d4')/10)
            elif curr_option == TERRITORIAL_STABILIZATION:
                log(f'{self._name} is stabilizing')
                self._instability *= random()
        self._power += bank

    def registry(self):
        self._age += 1
        if not self._territory:
            self._dissolve()
        self._powerbase = len(self._territory)  # For each unit of land you hold you gain extra power
        self._power += self._powerbase*(0.8+(roll('6d10-6d10')/100))+self._powerbase*self._techlevel*3  # National fortune = Fortune (normal distribution) + tech
        self._instability += randint(1, ceil(self._powerbase/10)+1) - roll('3d6-3d6')
        if roll('2d100') < self._instability:
            if roll('1d6') == 1:
                self._dissolve()
            else:
                if roll('1d6') < 4:
                    self._collapse()
                else:
                    self._collapse(natural=True)

    def _expand(self):
        if self._dead or not self._territory:
            return

        for _ in range(randint(2, 5)):
            attempt = choice(self._territory)
            rng = 1
            long = randint(clamp(attempt[1]-rng, nmax=self._world.width-1), clamp(attempt[1]+rng, nmax=self._world.width-1))
            lat = randint(clamp(attempt[0]-rng, nmax=self._world.height-1), clamp(attempt[0]+rng, nmax=self._world.height-1))
            attempt_coord = self._world.wgrid[lat][long]

            if not (attempt_coord == OCEAN or [lat, long] in self._territory):  # Cannot expand into water or own territory
                c = 10 + max(50, 5*self._techlevel)  # Base 10% success chance, max +50% from technology
                if attempt_coord == self._home_biome:  # Bonus chance for expansion if attempting to expand into base biome
                    c += 20
                if self._world.cgrid[lat][long] != UNOCCUPIED:  # Spreading into occupied squares is harder
                    emblem = self._world.cgrid[lat][long]
                    c -= 5 + find_civ(emblem).techlevel
                if self._world.wgrid[lat][long] == MOUNTAIN:  # Mountains make it hard to spread
                    c -= 5
                elif self._world.wgrid[lat][long] == GRASSLAND:  # Grasslands are easy to spread
                    c += 5

                if roll('1d100') < c:
                    self._world.cgrid[lat][long] = self._emblem
                    self._territory.append([lat, long])

    def _dissolve(self):
        from civsim.game_master import GameMaster

        self._dead = True
        # at this point we lose the reference to the civ, this is intentional unless in the future is needed
        GameMaster.civ_compendium.pop(self._emblem)
        if self._territory:
            log(f'{self._name} has dissolved! It lasted {self._age} years and achieved a tech level of {self._techlevel:.2f} and extended over {self._territory}')
            sweep_the_land(self._territory, self._world)
            n = randint(1, ceil(self._powerbase/10)+1)
            remanents = sample(self._territory, min(len(self._territory), n))
            for remanent in remanents:
                log(f'Remanents from {self._name} have appeared at {remanent}!')
                new_civ = type(self).born_civ(remanent[0], remanent[1], self._world)
                if not new_civ:
                    log(f'They could not survive...')
        else:
            log(f'{self._name} has dissolved! It lasted {self._age} years and achieved a tech level of {self._techlevel:.2f} and lost all its territory')
        type(self).civ_emblems += self._emblem # for now remanents can't take dissolved civilisation emblems as theirs to avoid confusion

    def _collapse(self, natural=False):
        """
        Look on my works, ye Mighty, and despair!

        """

        if natural:
            disaster = choice(DISASTERS)
            log(f'{self._name} suffers a {disaster}!')
        log(f'{self._name} with {self._powerbase} is collapsing!')
        self._instability += roll(f'{ceil(self._powerbase/10)}d6')
        self._power /= randint(2, 4)
        n = randint(floor(len(self._territory)/1.5), len(self._territory))
        rebels = sample(self._territory, min(len(self._territory), n))
        for rebel in rebels:
            log(f'Rebels from {self._name} have appeared at {rebel}!')
            self._territory.remove(rebel)
            self._world.cgrid[rebel[0]][rebel[1]] = UNOCCUPIED
        if not natural and rebels:  # Natural disasters do not create new states, rebels eventually will be pacified
            warlords = []
            try:
                n = randint(1, ceil(self._powerbase / 10) + 1)
                warlords = sample(rebels, min(len(rebels), n))
            except:
                raise Exception(f'{self._name} with powerbase {self._powerbase} suffers uprise by {rebels} sample {n}')
            new_civs = []
            # 2 steps to avoid warlords expanding into other warlords without civ generated yet
            for warlord in warlords:
                log(f'Rebels from {self._name} at {warlord} have chosen a warlord!')
                new_civ = type(self).born_civ(warlord[0], warlord[1], self._world, parent=self, expand=False)
                if new_civ:
                    new_civs.append(new_civ)
                else:
                    log(f'They failed misserably...')
            for civ in new_civs:
                civ._expand()
        if not self._territory:
            self._dissolve()

    @property
    def techlevel(self):
        return self._techlevel

    @property
    def emblem(self):
        return self._emblem

    @property
    def name(self):
        return self._name

    @property
    def territory(self):
        return self._territory

