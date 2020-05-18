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
@click.option('-t', '--ticker', metavar='TICKER',
              multiple=True, help="Stocks tickers to filter for")
def show(transactions_csv, ticker):
    transactions = TransactionsReader(transactions_csv).get_transactions()
    capgains_show(transactions, tickers=ticker)
