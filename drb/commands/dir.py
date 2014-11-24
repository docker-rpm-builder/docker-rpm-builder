import click
from drb.spawn import sp

@click.command()
@click.argument("imagetag", type=click.STRING)
@click.argument("source_directory", type=click.Path(exists=True, file_okay=False, resolve_path=True))
def dir(imagetag, directory):
    pass