import click
import tabulate


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

floatfmt = (
    None,    # date
    None,    # description
    None,    # ticker
    None,    # action
    None,    # qty
    ",.2f",  # price
    ",.2f",  # commission
    None,    # currency
)


def capgains_show(transactions, tickers=None):
    """Take a list of transactions and print them in tabular format."""
    filtered_transactions = transactions.filter_by(tickers=tickers)
    if not filtered_transactions:
        click.echo("No results found")
        return
    headers = ["date", "description", "ticker", "action", "qty", "price",
               "commission", "currency"]
    rows = [[
        t.date,
        t.description,
        t.ticker,
        t.action,
        t.qty,
        t.price,
        t.commission,
        t.currency
    ] for t in filtered_transactions]
    output = tabulate.tabulate(rows, headers=headers, colalign=colalign,
                               tablefmt="psql", floatfmt=floatfmt)
    click.echo(output)
