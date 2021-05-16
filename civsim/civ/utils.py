from civsim.civ.constants import UNOCCUPIED

def sweep_the_land(territory, world):
    for lat, long in territory:
        world.cgrid[lat][long] = UNOCCUPIED

def find_civ(emblem):
    from civsim.game_master import GameMaster

    found = GameMaster.civ_compendium.get(emblem, None)
    if not found:
        raise Exception(f'Could not found civilisation {emblem}')

    return found
