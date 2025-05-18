import click
import json
from itertools import groupby

from capgains.exchange_rate import ExchangeRate
from capgains.ticker_gains import TickerGains

# describes how to align the individual table columns
colalign = (
    "left",  # ticker
    "right",  # max cost
    "right",  # year end
)


def _get_max_cost(transactions, year, year_min):
    transactions_to_report = transactions.filter_by(year=year)

    max_cost = 0
    for t in transactions_to_report:
        max_cost = max(max_cost, t.cumulative_cost)

    # check against end of last year
    max_cost = max(
        max_cost, _get_year_end_cost(transactions, year - 1, year_min)
    )  # noqa: E501

    return max_cost


def _get_year_end_cost(transactions, year, year_min):
    transactions_to_report = transactions.filter_by(year=year)

    # if none this year, return last year
    if not transactions_to_report:
        # stop if we hit floor of years to check against
        if year <= year_min:
            return 0

        return _get_year_end_cost(transactions, year - 1, year_min)

    return transactions_to_report[len(transactions_to_report) -
                                  1].cumulative_cost  # noqa: E501


def _get_map_of_currencies_to_exchange_rates(transactions):
    """First, split the list of txs into sublists where each sublist
    will only contain transactions with the same currency."""

    contiguous_currencies = sorted(
        transactions.transactions, key=lambda t: t.currency
    )
    currency_groups = [
        list(g)
        for _, g in groupby(contiguous_currencies, lambda t: t.currency)
    ]
    currencies_to_exchange_rates = dict()
    # Create a separate ExchangeRate object for each currency
    for currency_group in currency_groups:
        currency = currency_group[0].currency
        min_date = currency_group[0].date
        max_date = currency_group[-1].date
        currencies_to_exchange_rates[currency] = ExchangeRate(
            currency, min_date, max_date
        )
    return currencies_to_exchange_rates


def calculate_costs(transactions, year, ticker):
    ticker_transactions = transactions.filter_by(
        tickers=[ticker], max_year=year
    )
    er_map = _get_map_of_currencies_to_exchange_rates(ticker_transactions)
    tg = TickerGains(ticker)
    tg.add_transactions(ticker_transactions, er_map)
    return ticker_transactions


def capgains_maxcost(transactions, year, tickers=None, output_format='table'):
    """Take a list of txs and output the calculated costs.

    Args:
        transactions: list of txs to process
        year: Year to calculate costs for
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
            transactions_to_report = calculate_costs(
                filtered_transactions, year, ticker
            )
            if not transactions_to_report:
                results[ticker] = {
                    'year': year, 'max_cost': 0, 'year_end_cost': 0
                }
                continue

            max_cost = _get_max_cost(
                transactions_to_report, year, transactions_to_report.year_min
            )
            year_end_cost = _get_year_end_cost(
                transactions_to_report, year, transactions_to_report.year_min
            )

            results[ticker] = {
                'year': year,
                'max_cost': float(max_cost),
                'year_end_cost': float(year_end_cost)
            }
        click.echo(json.dumps(results, indent=2))
        return

    # Original table output format
    for ticker in filtered_transactions.tickers:
        click.echo("{}-{}".format(ticker, year))
        transactions_to_report = calculate_costs(
            filtered_transactions, year, ticker
        )
        if not transactions_to_report:
            click.echo("Nothing to report\n")
            continue

        max_cost = _get_max_cost(
            transactions_to_report, year, transactions_to_report.year_min
        )
        year_end_cost = _get_year_end_cost(
            transactions_to_report, year, transactions_to_report.year_min
        )

        click.echo("[Max cost = {0:,.2f}]".format(max_cost))
        click.echo("[Year end = {0:,.2f}]\n".format(year_end_cost))
