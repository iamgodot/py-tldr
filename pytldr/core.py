from click import command, secho


@command()
def cli():
    secho('Hello world!', fg='green', bold=True)
