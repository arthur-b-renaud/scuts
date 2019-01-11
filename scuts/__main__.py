# -*- coding: utf-8 -*-
"""
@file
@brief Implements command line ``python -m scuts <command> <args>``.
"""
import sys
from pyquickhelper.cli import cli_main_helper


def main(args, fLOG=print):
    """
    Implements ``python -m scuts <command> <args>``.

    :param args: command line arguments
    :param fLOG: logging function

    Example::

        python -m scuts hash_file -f setup.cfg
    """
    try:
        from .utils import hash_file
    except ImportError:
        from scuts.utils import hash_file

    fcts = dict(hash_file=hash_file)
    return cli_main_helper(fcts, args=args, fLOG=fLOG)


if __name__ == "__main__":
    main(sys.argv[1:])
