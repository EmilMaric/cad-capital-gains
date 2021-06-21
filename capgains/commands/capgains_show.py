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
        "{0:f}".format(t.qty.normalize()),
        "{:,.2f}".format(t.price),
        "{:,.2f}".format(t.commission),
        t.currency
    ] for t in filtered_transactions]
    output = tabulate.tabulate(rows, headers=headers, colalign=colalign,
                               tablefmt="psql", disable_numparse=True)
    click.echo(output)
