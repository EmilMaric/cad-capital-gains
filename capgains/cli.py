import click

from capgains.commands.capgains_show import capgains_show
from capgains.commands.capgains_calc import capgains_calc
from capgains.transactions_reader import TransactionsReader


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


@capgains.command(help=("Calculates capital gains from the transactions "
                        "CSV-file and displays output in a tabular format. "
                        "Filters can be applied to select which stocks to "
                        "calculate the capital gains on."))
@click.argument('transactions-csv')
@click.argument('year', type=click.INT)
@click.option('-t', '--tickers', metavar='TICKERS',
              multiple=True, help="Stocks tickers to filter for")
def calc(transactions_csv, year, tickers):
    transactions = TransactionsReader.get_transactions(transactions_csv)
    capgains_calc(transactions, year, tickers=tickers)
