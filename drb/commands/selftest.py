# -*- coding: utf-8 -*-

import click

@click.command(help=_HELP)
@click.option("--full", is_flag=True)
def selftest(full=False):
    pass

