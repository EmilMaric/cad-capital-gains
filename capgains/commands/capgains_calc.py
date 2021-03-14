import click
import tabulate
from itertools import groupby

from capgains.exchange_rate import ExchangeRate
from capgains.ticker_gains import TickerGains

# describes how to align the individual table columns
colalign = (
    "left",   # date
    "left",   # description
    "left",   # ticker
    "left",   # qty
    "right",  # proceeds
    "right",  # acb
    "right",  # commission
    "right",  # capital gain
)

floatfmt = (
    None,    # date
    None,    # description
    None,    # ticker
    None,    # qty
    ",.2f",  # proceeds
    ",.2f",  # acb
    ",.2f",  # commission
    ",.2f",  # capital gain
)


def _get_total_gains(transactions):
    total = 0
    for t in transactions:
        total += t.capital_gain
    return total


def _get_map_of_currencies_to_exchange_rates(transactions):
    """First, split the list of transactions into sublists where each sublist
    will only contain transactions with the same currency"""
    currency_groups = [list(g) for _, g in groupby(transactions,
                                                   lambda t: t.currency)]
    currencies_to_exchange_rates = dict()
    # Create a separate ExchangeRate object for each currency
    for currency_group in currency_groups:
        currency = currency_group[0].currency
        min_date = currency_group[0].date
        max_date = currency_group[-1].date
        currencies_to_exchange_rates[currency] = ExchangeRate(
            currency, min_date, max_date)
    return currencies_to_exchange_rates


def calculate_gains(transactions, year, ticker):
    ticker_transactions = transactions.filter_by(tickers=[ticker],
                                                 max_year=year)
    er_map = _get_map_of_currencies_to_exchange_rates(ticker_transactions)
    tg = TickerGains(ticker)
    tg.add_transactions(ticker_transactions, er_map)
    return ticker_transactions.filter_by(year=year, action='SELL',
                                         superficial_loss=False)


def capgains_calc(transactions, year, tickers=None):
    """Take a list of transactions and print the calculated capital
    gains in a separate tabular format for each specified ticker."""
    filtered_transactions = transactions.filter_by(tickers=tickers)
    if not filtered_transactions:
        click.echo("No transactions available")
        return
    for ticker in filtered_transactions.tickers:
        click.echo("{}-{}".format(ticker, year))
        transactions_to_report = calculate_gains(filtered_transactions, year,
                                                 ticker)
        if not transactions_to_report:
            click.echo("No capital gains\n")
            continue
        total_gains = _get_total_gains(transactions_to_report)
        click.echo("[Total Gains = {0:,.2f}]".format(total_gains))
        headers = ["date", "description", "ticker", "qty", "proceeds", "ACB",
                   "outlays", "capital gain/loss"]
        rows = [[
            t.date,
            t.description,
            t.ticker,
            t.qty,
            t.proceeds,
            t.acb,
            t.expenses,
            t.capital_gain
        ] for t in transactions_to_report]
        output = tabulate.tabulate(rows, headers=headers, tablefmt="psql",
                                   colalign=colalign, floatfmt=floatfmt)
        click.echo("{}\n".format(output))
