import random
from civsim.third.rpgtools import main as rpgtools

from civsim.config import GAME_MODE, HEIGHT, MENU_LOGO, PIONERS, WIDTH
from civsim.game_master import GameMaster
from civsim.scripts.utils import DefaultArgumentParser, initialize_params
from civsim.__version__ import __version__


def main():
    parser = DefaultArgumentParser()
    args = parser.parse_args()

    print(MENU_LOGO)
    print(f'Civsim {__version__} by UtilityHotbar')
    mode = rpgtools.generate_menu(GAME_MODE)

    initialize_params(args)
    gm = GameMaster(mode, args.debug)
    gm.creation(HEIGHT, WIDTH, PIONERS)
    gm.display()
    gm.hourglass()
