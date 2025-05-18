import click
import tabulate
import json
from itertools import groupby

from capgains.exchange_rate import ExchangeRate


# describes how to align the individual table columns
colalign = (
    "left",   # date
    "left",   # description
    "left",   # ticker
    "left",   # action
    "right",  # qty
    "right",  # price
    "right",  # commission
    "right",  # currency
)


def _transaction_to_dict(transaction, show_exchange_rate=False):
    """Convert a transaction to a dictionary for JSON output"""
    result = {
        'date': transaction.date.isoformat(),
        'description': transaction.description,
        'ticker': transaction.ticker,
        'action': transaction.action,
        'quantity': float(transaction.qty.normalize()),
        'price': float(transaction.price),
        'commission': float(transaction.commission),
        'currency': transaction.currency
    }
    if show_exchange_rate:
        result['exchange_rate'] = float(transaction.exchange_rate)
    return result


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


def _add_rates(transactions, exchange_rates):
    for t in transactions:
        t.add_rate(exchange_rates)


def capgains_show(transactions, show_exchange_rate, tickers=None, output_format='table'):
    """Take a list of transactions and output them in the specified format.
    
    Args:
        transactions: List of transactions to show
        show_exchange_rate: Whether to include exchange rates
        tickers: Optional list of tickers to filter by
        output_format: Output format ('table' or 'json')
    """
    filtered_transactions = transactions.filter_by(tickers=tickers)

    if not filtered_transactions:
        if output_format == 'json':
            click.echo(json.dumps({'error': 'No results found'}))
        else:
            click.echo("No results found")
        return

    if show_exchange_rate:
        er_map = _get_map_of_currencies_to_exchange_rates(filtered_transactions)
        _add_rates(filtered_transactions, er_map)

    if output_format == 'json':
        results = {
            'transactions': [_transaction_to_dict(t, show_exchange_rate) for t in filtered_transactions]
        }
        click.echo(json.dumps(results, indent=2))
        return

    # Original table output format
    headers = None
    rows = None
    if show_exchange_rate:
        headers = ["date", "description", "ticker", "action", "qty", "price",
                   "commission", "currency", "exchange"]
        rows = [[
            t.date,
            t.description,
            t.ticker,
            t.action,
            "{0:f}".format(t.qty.normalize()),
            "{:,.2f}".format(t.price),
            "{:,.2f}".format(t.commission),
            t.currency,
            t.exchange_rate
        ] for t in filtered_transactions]
    else:
        headers = ["date", "description", "ticker", "action", "qty", "price",
                   "commission", "currency"]
        rows = [[
            t.date,
            t.description,
            t.ticker,
            t.action,
            "{0:f}".format(t.qty.normalize()),
            "{:,.2f}".format(t.price),
            "{:,.2f}".format(t.commission),
            t.currency
        ] for t in filtered_transactions]

    output = tabulate.tabulate(rows, headers=headers, colalign=colalign,
                               tablefmt="psql", disable_numparse=True)
    click.echo(output)
