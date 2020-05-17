import click
import capgains.commands.capgains_show as CapGainsShow


@click.group()
def capgains():
    pass


@capgains.command()
@click.option('-t', '--ticker', multiple=True)
def show(ticker):
    CapGainsShow.show_cap_gains(ticker)
    pass
