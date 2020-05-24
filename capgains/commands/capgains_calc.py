import click
import tabulate
import requests
from datetime import datetime, timedelta
from capgains.exchange_rate import ExchangeRate
from capgains.ticker_gains import TickerGains

# describes how to align the individual table columns
colalign = (
    "left",   # date
    "left",   # transaction_type
    "left",   # ticker
    "left",   # action
    "right",  # qty
    "right",  # price
    "right",  # commission
    "right",  # share_balance
    "right",  # proceeds
    "right",  # capital_gain
    "right",  # acb_delta
    "right",  # acb
)

floatfmt = (
    None,   # date
    None,   # transaction_type
    None,   # ticker
    None,   # action
    None,  # qty
    ",.2f",  # price
    ",.2f",  # commission
    None,  # share_balance
    ",.2f",  # proceeds
    ",.2f",  # capital_gain
    ",.2f",  # acb_delta
    ",.2f",  # acb
)

def _filter_transaction(transaction, ticker):
    if transaction.ticker != ticker:
        return False
    return True


def _filter_calculated_transaction(transaction, year):
    if transaction.date.year != year:
        return False
    if transaction.action != 'SELL':
        return False
    return True


def capgains_calc(transactions, year, tickers=None):
    """Take a list of transactions and print them in tabular format."""
    calculation_made = False

    if not tickers:
        tickers = set([transaction.ticker for transaction in transactions])
        
    for ticker in tickers:
        # prune transactions that don't match the filter options
        filtered_transactions = list(filter(
            lambda t: _filter_transaction(t, ticker=ticker), transactions))
        if not filtered_transactions:
            continue
        er = ExchangeRate('USD', transactions[0].date, transactions[-1].date)
        tg = TickerGains(ticker)
        for transaction in filtered_transactions:
            rate = er.get_rate(transaction.date)
            tg.add_transaction(transaction, rate)
        year_transactions = list(filter(
            lambda t: _filter_calculated_transaction(t, year),
                      filtered_transactions))
        transaction_dicts = [t.to_dict(all_values=True) for t in year_transactions]
        if not year_transactions:
            continue
        calculation_made = True
        headers = transaction_dicts[0].keys()
        rows = [t.values() for t in transaction_dicts]
        output = tabulate.tabulate(rows, headers=headers,
                                   colalign=colalign, floatfmt=floatfmt)
        click.echo("{}-{}".format(ticker,year))
        click.echo("{}\n".format(output))
    if not calculation_made:
        click.echo("No calculations made")
