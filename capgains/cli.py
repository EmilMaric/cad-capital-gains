import click

from .commands.capgains_show import capgains_show
from .transactions_reader import TransactionsReader


@click.group()
def capgains():
    pass


@capgains.command(help=("Show entries from the transactions CSV-file in a "
                        "tabular format. Filters can be applied to narrow "
                        "down the entries."))
@click.argument('transactions-csv')
@click.option('-t', '--tickers', metavar='TICKERS',
              multiple=True, help="Stocks tickers to filter for")
def show(transactions_csv, tickers):
    transactions = TransactionsReader.get_transactions(transactions_csv)
    capgains_show(transactions, tickers)
