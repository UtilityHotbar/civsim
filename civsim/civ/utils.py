"""Miscellaneous Civilisation methods."""

from civsim.civ.constants import UNOCCUPIED


def sweep_the_land(territory, world):
    """Set all the territory from a world as UNOCUPPIED."""
    for lat, long in territory:
        world.cgrid[lat][long] = UNOCCUPIED


def find_civ(emblem):
    """Return the civ given a emblem if exists."""
    from civsim.game_master import GameMaster

    found = GameMaster.civ_compendium.get(emblem, None)
    if not found:
        raise Exception(f'Could not find civilisation {emblem}')

    return found
