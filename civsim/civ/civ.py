"""Module related with all the civilisation generation stuff."""

from math import ceil, floor
from random import choice, randint, random, sample

from civsim.civ.constants import (CIV_PRIORITIES, COMMONS_WORLD_PATH,
                                  LANG_STRUCT_PATH, POPULATION_GROWTH,
                                  TECH_DEVELOPMENT, TERRITORIAL_EXPANSION,
                                  TERRITORIAL_STABILIZATION, UNOCCUPIED)
from civsim.civ.utils import find_civ, sweep_the_land
from civsim.third.rpgtools import lang_gen, table_process
from civsim.third.rpgtools.main import generate_menu, roll
from civsim.utils import clamp, log
from civsim.world.constants import DISASTERS, GRASSLAND, MOUNTAIN, OCEAN


class Civilisation:
    """A class to build a civilisation."""

    # TODO this class needs to be remade if multithread civs are added or multiplanets

    civ_ptr = 0
    civ_emblems = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()-_=+[{]}\\|;:,<.>/?'

    def __init__(self, name, emblem, origin, world, ancestor=None, cpu=True):
        """Initialize civ parameters."""
        self._language = lang_gen.make_language(COMMONS_WORLD_PATH, table_process.Table(LANG_STRUCT_PATH))
        self._name = self._language.brute_force_translate(name)
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
        self._base_power = 1
        self._tech_level = 0

        # Internal priorities
        self._priorities = [item for priority in CIV_PRIORITIES for item in (priority,) * randint(1, 8)]

        # Diplomatic profile
        self._profile = {
            'friendliness': roll('1d100'),
            'trustworthiness': roll('1d100'),
            'fearfulness': roll('1d100'),
            'reputation': 0,
        }

        # Diplomatic relationships
        self._relationships = {}

    def __str__(self):
        """Ostende te!."""
        return (f'{self._name} [{self._emblem}] governs over {self._territory} with its homeland biome'
                '{self._home_biome}')

    @classmethod
    def born_civ(cls, lat, long, world, parent=None, expand=False, cpu=True):
        """There is no salvation for us but to adopt Civilization and lift ourselves down to its level."""
        from civsim.game_master import GameMaster

        if cls.civ_ptr > len(cls.civ_emblems)-1:
            return
        world.cgrid[lat][long] = cls.civ_emblems[cls.civ_ptr]
        sprout = cls(f'{cls.civ_emblems[cls.civ_ptr]}+{cls.civ_ptr}',
                     cls.civ_emblems[cls.civ_ptr], [lat, long], world, parent, cpu)
        if cpu:
            log(f'A new civilization {sprout.name} appeared at {[lat, long]}')
        else:
            log(f'A new civilization {sprout.name} appeared at {[lat, long]} controlled by the player')
        cls.civ_ptr += 1
        if expand:
            sprout._expand()
        GameMaster.civ_compendium[sprout.emblem] = sprout

        return sprout

    def actions(self):
        """Civilization is made -- or destroyed -- by its articulate voices."""
        bank = 0
        base_actions = ceil(self._base_power/10+1)
        max_actions = ceil(self._base_power/5+1)
        curr_actions = randint(base_actions, max_actions)
        if not self._cpu:
            print(f'Son of {self._name} [{self._emblem}] which is your next move?\n'
                  f'Power: {self._power:.2f} (Grow or expand to increase your power)\n'
                  f'Territory: {self._base_power} (Expanding requires 10 power)\n'
                  f'Tech level: {self._tech_level:.2f} (Development requires 20 power)\n'
                  f'Instability: {self._instability:.2f} (Decreasing instability is free)\n')
        for n in range(curr_actions):
            if not self._cpu:
                print(f'YOU HAVE {curr_actions-n} ACTIONS REMAINING')
                curr_option = CIV_PRIORITIES[generate_menu(CIV_PRIORITIES)]
            else:
                curr_option = choice(self._priorities)
            if curr_option == TERRITORIAL_EXPANSION:
                log(f'{self._name} [{self._emblem}] is expanding')
                if self._power > 10:
                    self._power -= 10
                    self._expand()
                else:
                    log(f'{self._name} [{self._emblem}] failed to expand')
            elif curr_option == TECH_DEVELOPMENT:
                log(f'{self._name} [{self._emblem}] is developing')
                if self._power > 20:
                    self._power -= 20
                    self._tech_level += roll('1d10')/10
                else:
                    log(f'{self._name} [{self._emblem}] failed to develop')
            elif curr_option == POPULATION_GROWTH:
                log(f'{self._name} [{self._emblem}] is growing')
                bank += self._power * (roll('1d4')/10)
            elif curr_option == TERRITORIAL_STABILIZATION:
                log(f'{self._name} [{self._emblem}] is stabilizing')
                self._instability *= random()
        self._power += bank

    def cadastre(self):
        """Order a real state's metes-and-bounds cadastral map to be set up."""
        self._age += 1
        if not self._territory:
            self._dissolve()
        self._base_power = len(self._territory)  # For each unit of land you hold you gain extra power
        self._power += self._base_power*(0.8+(roll('6d10-6d10')/100))+self._base_power * \
            self._tech_level*3  # National fortune = Fortune (normal distribution) + tech
        self._instability += randint(1, ceil(self._base_power/10)+1) - roll('3d6-3d6')
        if roll('2d100') < self._instability:
            if roll('1d6') == 1:
                self._dissolve()
            else:
                if roll('1d6') < 4:
                    self._collapse()
                else:
                    self._collapse(natural=True)

    def _expand(self):
        """We must annex those people. We can afflict them with our wise and beneficent government."""
        if self._dead or not self._territory:
            return

        for _ in range(randint(2, 5)):
            attempt = choice(self._territory)
            rng = 1
            long = randint(clamp(attempt[1]-rng, nmax=self._world.width-1),
                           clamp(attempt[1]+rng, nmax=self._world.width-1))
            lat = randint(clamp(attempt[0]-rng, nmax=self._world.height-1),
                          clamp(attempt[0]+rng, nmax=self._world.height-1))
            attempt_coord = self._world.wgrid[lat][long]

            # Cannot expand into water or own territory
            if not (attempt_coord == OCEAN or [lat, long] in self._territory):
                c = 10 + max(50, 5*self._tech_level)  # Base 10% success chance, max +50% from technology
                if attempt_coord == self._home_biome:  # Bonus chance if attempting to expand into base biome
                    c += 20
                if self._world.cgrid[lat][long] != UNOCCUPIED:  # Spreading into occupied squares is harder
                    emblem = self._world.cgrid[lat][long]
                    c -= 5 + find_civ(emblem).tech_level
                if self._world.wgrid[lat][long] == MOUNTAIN:  # Mountains make it hard to spread
                    c -= 5
                elif self._world.wgrid[lat][long] == GRASSLAND:  # Grasslands are easy to spread
                    c += 5

                if roll('1d100') < c:
                    self._world.cgrid[lat][long] = self._emblem
                    self._territory.append([lat, long])

    def _dissolve(self):
        """Every civilization carries the seeds of its own destruction."""
        from civsim.game_master import GameMaster

        self._dead = True
        # at this point we lose the reference to the civ, this is intentional unless in the future is needed
        GameMaster.civ_compendium.pop(self._emblem)
        if self._territory:
            log(f'{self._name} [{self._emblem}] has dissolved! It lasted {self._age} years and achieved a tech level of'
                ' {self._tech_level: .2f} and extended over {self._territory}')
            sweep_the_land(self._territory, self._world)
            n = randint(1, ceil(self._base_power/10)+1)
            remanents = sample(self._territory, min(len(self._territory), n))
            for remanent in remanents:
                log(f'Remanents from {self._name} [{self._emblem}] have appeared at {remanent}!')
                new_civ = type(self).born_civ(remanent[0], remanent[1], self._world)
                if not new_civ:
                    log('They could not survive...')
        else:
            log(f'{self._name} [{self._emblem}] has dissolved! It lasted {self._age} years and achieved a tech level of'
                ' {self._tech_level:.2f} and lost all its territory')
        # for now remanents can't take dissolved civilisation emblems as theirs to avoid confusion
        type(self).civ_emblems += self._emblem

    def _collapse(self, natural=False):
        """Look on my works, ye Mighty, and despair!."""
        if natural:
            disaster = choice(DISASTERS)
            log(f'{self._name} [{self._emblem}] suffers a {disaster}!')
        log(f'{self._name} [{self._emblem}] with {self._base_power} is collapsing!')
        self._instability += roll(f'{ceil(self._base_power/10)}d6')
        self._power /= randint(2, 4)
        n = randint(floor(len(self._territory)/1.5), len(self._territory))
        rebels = sample(self._territory, min(len(self._territory), n))
        for rebel in rebels:
            log(f'Rebels from {self._name} [{self._emblem}] have appeared at {rebel}!')
            self._territory.remove(rebel)
            self._world.cgrid[rebel[0]][rebel[1]] = UNOCCUPIED
        if not natural and rebels:  # Natural disasters do not create new states, rebels eventually will be pacified
            warlords = []
            try:
                n = randint(1, ceil(self._base_power / 10) + 1)
                warlords = sample(rebels, min(len(rebels), n))
            except ValueError:
                raise Exception(f'{self._name} [{self._emblem}] with powerbase {self._base_power} suffers uprise by'
                                '{rebels} sample {n}')
            new_civs = []
            # 2 steps to avoid warlords expanding into other warlords without civ generated yet
            for warlord in warlords:
                log(f'Rebels from {self._name} [{self._emblem}] at {warlord} have chosen a warlord!')
                new_civ = type(self).born_civ(warlord[0], warlord[1], self._world, parent=self, expand=False)
                if new_civ:
                    new_civs.append(new_civ)
                else:
                    log('They failed misserably...')
            for civ in new_civs:
                civ._expand()
        if not self._territory:
            self._dissolve()

    @property
    def tech_level(self):
        """Return civilisation's tech_level."""
        return self._tech_level

    @property
    def emblem(self):
        """Return civilisation's emblem."""
        return self._emblem

    @property
    def name(self):
        """Return civilisation's name."""
        return self._name

    @property
    def territory(self):
        """Return civilisation's territory."""
        return self._territory
