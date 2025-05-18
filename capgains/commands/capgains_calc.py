import click
import tabulate
import json
from itertools import groupby

from capgains.exchange_rate import ExchangeRate
from capgains.ticker_gains import TickerGains

# describes how to align the individual table columns
colalign = (
    "left",   # date
    "left",   # description
    "left",   # ticker
    "right",  # qty
    "right",  # proceeds
    "right",  # acb
    "right",  # commission
    "right",  # capital gain
)


def _transaction_to_dict(transaction):
    """Convert a transaction to a dictionary for JSON output"""
    return {
        'date': transaction.date.isoformat(),
        'description': transaction.description,
        'ticker': transaction.ticker,
        'quantity': float(transaction.qty.normalize()),
        'proceeds': float(transaction.proceeds),
        'acb': float(transaction.acb),
        'outlays': float(transaction.expenses),
        'capital_gain': float(transaction.capital_gain)
    }


def _get_total_gains(transactions):
    total = 0
    for t in transactions:
        total += t.capital_gain
    return total


def _get_map_of_currencies_to_exchange_rates(transactions):
    """First, split the list of transactions into sublists where each sublist
    will only contain transactions with the same currency"""

    contiguous_currencies = sorted(transactions.transactions,
                                   key=lambda t: t.currency)
    currency_groups = [list(g) for _, g in groupby(contiguous_currencies,
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


def capgains_calc(transactions, year, tickers=None, output_format='table'):
    """Take a list of transactions and output the calculated capital gains.
    
    Args:
        transactions: List of transactions to process
        year: Year to calculate gains for
        tickers: Optional list of tickers to filter by
        output_format: Output format ('table' or 'json')
    """
    filtered_transactions = transactions.filter_by(tickers=tickers)
    if not filtered_transactions:
        if output_format == 'json':
            click.echo(json.dumps({'error': 'No transactions available'}))
        else:
            click.echo("No transactions available")
        return

    if output_format == 'json':
        results = {}
        for ticker in filtered_transactions.tickers:
            transactions_to_report = calculate_gains(filtered_transactions, year, ticker)
            if not transactions_to_report:
                results[ticker] = {
                    'year': year,
                    'total_gains': 0,
                    'transactions': []
                }
                continue
            
            total_gains = _get_total_gains(transactions_to_report)
            results[ticker] = {
                'year': year,
                'total_gains': float(total_gains),
                'transactions': [_transaction_to_dict(t) for t in transactions_to_report]
            }
        click.echo(json.dumps(results, indent=2))
        return

    # Original table output format
    for ticker in filtered_transactions.tickers:
        click.echo("{}-{}".format(ticker, year))
        transactions_to_report = calculate_gains(filtered_transactions, year, ticker)
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
            "{0:f}".format(t.qty.normalize()),
            "{:,.2f}".format(t.proceeds),
            "{:,.2f}".format(t.acb),
            "{:,.2f}".format(t.expenses),
            "{:,.2f}".format(t.capital_gain)
        ] for t in transactions_to_report]
        output = tabulate.tabulate(rows, headers=headers, tablefmt="psql",
                                   colalign=colalign, disable_numparse=True)
        click.echo("{}\n".format(output))
