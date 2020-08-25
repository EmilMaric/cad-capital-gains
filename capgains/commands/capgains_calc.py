import click
import tabulate
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
    None,    # date
    None,    # transaction_type
    None,    # ticker
    None,    # action
    None,    # qty
    ",.2f",  # price
    ",.2f",  # commission
    None,    # share_balance
    ",.2f",  # proceeds
    ",.2f",  # capital_gain
    ",.2f",  # acb_delta
    ",.2f",  # acb
)


def _filter_transaction(transaction, max_year, ticker):
    if transaction.ticker != ticker:
        return False
    if transaction.date.year > max_year:
        return False
    return True


def _filter_calculated_transaction(transaction, year):
    # Only display 'SELL' transactions of the current year
    if transaction.date.year != year:
        return False
    if transaction.action != 'SELL':
        return False
    return True


def get_calculated_dicts(transactions, year, ticker):
    """Prune transactions that don't match the filter options:
    1) We need all the transactions prior to the max_year in order
       to calculate ACB
    2) We only care about the selected ticker"""
    filtered_transactions = list(filter(
        lambda t: _filter_transaction(t, max_year=year, ticker=ticker),
        transactions))
    if not filtered_transactions:
        return None
    er = ExchangeRate('USD', transactions[0].date, transactions[-1].date)
    tg = TickerGains(ticker)
    for transaction in filtered_transactions:
        rate = er.get_rate(transaction.date)
        tg.add_transaction(transaction, rate)
    year_transactions = list(filter(
        lambda t: _filter_calculated_transaction(t, year),
        filtered_transactions))
    if not year_transactions:
        return None
    return [t.to_dict(calculated_values=True) for t in year_transactions]


def capgains_calc(transactions, year, tickers=None):
    """Take a list of transactions and print the calculated capital
    gains in a separate tabular format for each specified ticker."""
    calculation_made = False
    if not tickers:
        tickers = set([transaction.ticker for transaction in transactions])
    for ticker in tickers:
        calculated_dicts = get_calculated_dicts(transactions, year, ticker)
        if not calculated_dicts:
            continue
        calculation_made = True
        headers = calculated_dicts[0].keys()
        rows = [t.values() for t in calculated_dicts]
        output = tabulate.tabulate(rows, headers=headers,
                                   colalign=colalign, floatfmt=floatfmt)
        click.echo("{}-{}".format(ticker, year))
        click.echo("{}\n".format(output))
    if not calculation_made:
        click.echo("No calculations made")
