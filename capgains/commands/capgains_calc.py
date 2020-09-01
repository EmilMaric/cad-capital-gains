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


def _get_map_of_currencies_to_exchange_rates(transactions):
    currency_date_ranges = dict()
    # First, map the currency to a range of dates it needs
    for transaction in transactions:
        currency = transaction.currency
        date = transaction.date
        if currency not in currency_date_ranges:
            currency_date_ranges[currency] = (date, date)
        elif date < currency_date_ranges[currency][0]:
            currency_date_ranges[currency] = \
                (date, currency_date_ranges[currency][1])
        elif date > currency_date_ranges[currency][1]:
            currency_date_ranges[currency] = \
                (currency_date_ranges[currency][0], date)
    currencies_to_exchange_rates = dict()
    # Next, map the currency to an ExchangeRate object
    for currency in currency_date_ranges.keys():
        first_date = currency_date_ranges[currency][0]
        last_date = currency_date_ranges[currency][1]
        currencies_to_exchange_rates[currency] = \
            ExchangeRate(currency, first_date, last_date)
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
        headers = calculated_dicts[0].keys()
        rows = [t.values() for t in calculated_dicts]
        output = tabulate.tabulate(rows, headers=headers,
                                   colalign=colalign, floatfmt=floatfmt)
        click.echo("{}\n".format(output))
