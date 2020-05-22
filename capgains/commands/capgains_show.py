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
    transactions_dict = [t.to_dict() for t in filtered_transactions]
    headers = transactions_dict[0].keys()
    rows = [t.values() for t in transactions_dict]
    output = tabulate.tabulate(rows, headers=headers, disable_numparse=True,
                               colalign=colalign)
    click.echo(output)
