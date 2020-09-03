import click
import tabulate
from itertools import groupby

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
    "right",  # currency
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
    None,    # currency
    None,    # share_balance
    ",.2f",  # proceeds
    ",.2f",  # capital_gain
    ",.2f",  # acb_delta
    ",.2f",  # acb
)


def _filter_transaction(transaction, max_year, ticker):
    """Prune transactions that don't match the filter options:
    1) We need all the transactions prior to the max_year in order
       to calculate ACB
    2) We only care about the selected ticker"""
    if transaction.ticker != ticker:
        return False
    if transaction.date.year > max_year:
        return False
    return True


def _filter_calculated_transaction(transaction, year):
    # Only display transactions in the current year
    if transaction.date.year != year:
        return False
    # 'SELL' transactions are the only ones that contribute to gain/loss
    if transaction.action != 'SELL':
        return False
    # Only non superficial loss transactions
    if transaction.superficial_loss:
        return False
    return True


def _get_total_gains(calculated_dicts):
    total = 0
    for calculated_dict in calculated_dicts:
        total += calculated_dict['capital_gain']
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


def get_calculated_dicts(transactions, year, ticker):
    filtered_transactions = list(filter(
        lambda t: _filter_transaction(t, max_year=year, ticker=ticker),
        transactions))
    if not filtered_transactions:
        return None
    er_map = _get_map_of_currencies_to_exchange_rates(transactions)
    tg = TickerGains(ticker)
    tg.add_transactions(filtered_transactions, er_map)
    year_transactions = list(filter(
        lambda t: _filter_calculated_transaction(t, year),
        filtered_transactions))
    if not year_transactions:
        return None
    return [t.to_dict(calculated_values=True) for t in year_transactions]


def capgains_calc(transactions, year, tickers=None):
    """Take a list of transactions and print the calculated capital
    gains in a separate tabular format for each specified ticker."""
    if not transactions:
        click.echo("No transactions available")
        return
    if not tickers:
        # remove duplicates
        tickers = set([transaction.ticker for transaction in transactions])
        # order by ticker name
        tickers = list(tickers)
        tickers.sort()
    for ticker in tickers:
        click.echo("{}-{}".format(ticker, year))
        calculated_dicts = get_calculated_dicts(transactions, year, ticker)
        if not calculated_dicts:
            click.echo("No capital gains\n")
            continue
        total_gains = _get_total_gains(calculated_dicts)
        click.echo("[Total Gains = {0:,.2f}]".format(total_gains))
        headers = calculated_dicts[0].keys()
        rows = [t.values() for t in calculated_dicts]
        output = tabulate.tabulate(rows, headers=headers, tablefmt="psql",
                                   colalign=colalign, floatfmt=floatfmt)
        click.echo("{}\n".format(output))
