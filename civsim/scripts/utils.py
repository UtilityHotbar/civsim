"""Miscellaneous Scripts methods."""

import argparse


class DefaultArgumentParser(argparse.ArgumentParser):
    """Parse arguments from scripts."""

    def __init__(self, *args, **kwargs):
        """Initialize command arguments for scripts."""
        super().__init__(*args, **kwargs)
        self.add_argument('--debug', help='Debug mode', action='store_true')
        self.add_argument('--seed', help='Set seed to initialize the random number generator', type=float, default=None)
        self.add_argument('--age', help='Year when the simulation will stop', type=int)


def initialize_params(args):
    """Initialize game settings given one or more args."""
    # TODO create config class
    return None
