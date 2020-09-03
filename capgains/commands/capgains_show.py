import click
import tabulate


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
)


def _filter_transaction(transaction, tickers=None):
    if tickers and transaction.ticker not in tickers:
        return False
    return True


def capgains_show(transactions, tickers=None):
    """Take a list of transactions and print them in tabular format."""
    # prune transactions that don't match the filter options
    filtered_transactions = list(filter(
        lambda t: _filter_transaction(t, tickers=tickers), transactions))
    if not filtered_transactions:
        click.echo("No results found")
        return
    transaction_dicts = [t.to_dict() for t in filtered_transactions]
    headers = transaction_dicts[0].keys()
    rows = [t.values() for t in transaction_dicts]
    output = tabulate.tabulate(rows, headers=headers, colalign=colalign,
                               tablefmt="psql", floatfmt=floatfmt)
    click.echo(output)
