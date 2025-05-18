Canadian Capital Gains CLI Tool
=
[![Build Status](https://travis-ci.org/EmilMaric/cad-capital-gains.svg?branch=master)](https://travis-ci.org/EmilMaric/cad-capital-gains)
[![codecov](https://codecov.io/gh/EmilMaric/cad-capital-gains/branch/master/graph/badge.svg)](https://codecov.io/gh/EmilMaric/cad-capital-gains)

⚠️ **IMPORTANT LEGAL NOTICE**: This software is provided "as is" without any warranties. By using this software, you agree to the terms outlined in [LEGAL.md](LEGAL.md). Users MUST read and agree to these terms before using the software.

## Overview
Calculating your capital gains and tracking your adjusted cost base (ACB) manually, or using an Excel document, often proves to be a laborious process. This CLI tool calculates your capital gains and ACB for you, and just requires a CSV file with basic information about your transactions. The idea with this tool is that you are able to more or less cut-and-copy the output that it genarates and copy it into whatever tax filing software you end up using.

## Features:
- Supports transactions with multiple different stock tickers in the same CSV file, and outputs them in separate tables.
- Currently supports transactions done in both USD and CAD. For USD transactions, the daily exchange rate will be automatically fetched from the Bank of Canada.
- Will automatically apply [superficial capital loss](https://www.canada.ca/en/revenue-agency/services/tax/individuals/topics/about-your-tax-return/tax-return/completing-a-tax-return/personal-income/line-127-capital-gains/capital-losses-deductions/what-a-superficial-loss.html) rules when calculating your capital gains and ACB. This tool only supports full superficial capital losses, and does not support partial superficial losses. In sales with a superficial capital loss, the capital loss will be carried forward as perscribed by the CRA. A sale with a capital loss will be treated as superficial if it satisifies the following:
    - Shares with the same ticker were bought in the 61 day window (30 days before or 30 days after the sale)
    - There is a non-zero balance of shares sharing the same ticker at the end of the 61 day window (30 days after the sale)
- Outputs the running adjusted cost base (ACB) for every transaction with a non-superficial capital gain/loss
- Supports fractional quantities of shares

## T1135 Foreign Income Verification Statement
The T1135 form is a requirement from the Canada Revenue Agency (CRA) for Canadian residents who own specified foreign property with a total cost of more than CAD $100,000 at any time during the tax year. This includes foreign securities held in Canadian brokerage accounts.

### When is T1135 Required?
You must file a T1135 if:
- You are a Canadian resident for tax purposes
- You owned specified foreign property (including foreign stocks) with a total cost exceeding CAD $100,000 at any time during the year
- The securities are held for investment purposes (not personal use)

### How This Tool Helps with T1135
This tool provides the `maxcost` command to help with T1135 reporting:
```bash
$ capgains maxcost sample.csv 2023
```
This command will:
- Calculate the maximum cost of your foreign securities during the tax year
- Show the maximum cost in CAD using official Bank of Canada exchange rates
- Alert you if your holdings exceed the T1135 reporting threshold
- Break down the maximum cost by ticker for detailed reporting

### Important Notes:
- The tool uses the Bank of Canada's noon rates (pre-2017) and indicative rates (post-2017) for currency conversion
- Maximum cost is calculated based on the adjusted cost base (ACB) of your holdings
- The tool considers both buying and selling activities throughout the year
- If your maximum cost exceeds CAD $100,000, ensure you file form T1135 with your tax return to avoid penalties

# Installation and Setup

## Quick Install
```bash
# To get the latest release
pip install cad-capgains
```

## Try it with Sample Data
The package includes a comprehensive sample dataset in `tests/sample.csv` that you can use to try out the tool. After installation, you can run:
```bash
# Show all transactions
capgains show tests/sample.csv

# Show specific stock transactions
capgains show tests/sample.csv -t AAPL

# Calculate capital gains for 2023
capgains calc tests/sample.csv 2023

# Check maximum cost for T1135 reporting
capgains maxcost tests/sample.csv 2023
```

The sample data includes:
- Multiple years of transactions (2022-2024)
- Both USD and CAD stocks
- Various transaction types (buys, sells, partial sells)
- Multiple tickers (AAPL, GOOGL, TD.TO, etc.)

## Development Setup
For development, you can use the provided setup script:
```bash
# Clone the repository
git clone <repository-url>
cd cad-capital-gains

# Run the setup script
source scripts/envsetup.sh
```

The setup script will:
- Ensure pyenv is configured
- Install Poetry if not present
- Set up the development environment
- Install all dependencies

# CSV File Requirements
To start, create a CSV file that will contain all of your transactions. In the CSV file, each line will represent a `BUY` or `SELL` transaction.  Your transactions **must be in order**, with the oldest transactions coming first, followed by newer transactions coming later. The format is as follows:
```csv
<yyyy-mm-dd>,<description>,<stock_ticker>,<action(BUY/SELL)>,<quantity>,<price>,<commission>,<currency>
```

A comprehensive sample CSV file with various transaction scenarios (including both CAD and USD transactions, multiple tickers, and various transaction types) is available in the `tests/sample.csv` file. You can use this as a reference for formatting your own transaction file.

Here is a simple example:
```csv
# sample.csv
2017-2-15,ESPP PURCHASE,GOOG,BUY,100,50.00,10.00,USD
2017-5-20,RSU VEST,GOOG,SELL,50,45.00,0.00,CAD
```

**NOTE: This tool only supports calculating ACB and capital gains with transactions
dating from May 1, 2007 and onwards.**

# Usage
To show the CSV file in a nice tabular format you can run:
```bash
$ capgains show tests/sample.csv
+------------+--------------------+----------+----------+-------+----------+--------------+------------+
| date       | description        | ticker   | action   |   qty |    price |   commission |   currency |
|------------+--------------------+----------+----------+-------+----------+--------------+------------|
| 2022-01-15 | Initial Purchase   | AAPL     | BUY      |   100 |   142.50 |         9.99 |        USD |
| 2022-02-10 | Buy Canadian Bank  | TD.TO    | BUY      |   150 |    78.25 |         9.99 |        CAD |
| 2022-03-20 | Buy Tech           | GOOGL    | BUY      |    20 | 2,200.00 |         9.99 |        USD |
| 2022-04-15 | Buy ETF            | VFV.TO   | BUY      |   200 |    92.50 |         9.99 |        CAD |
| 2022-05-01 | Partial Sell       | AAPL     | SELL     |    30 |   165.00 |         9.99 |        USD |
+------------+--------------------+----------+----------+-------+----------+--------------+------------+
```
To calculate the capital gains you can run:
```bash
$ capgains calc tests/sample.csv 2023
AAPL-2023
[Total Gains = 4,714.97]
+------------+--------------------+----------+-------+------------+-----------+-----------+---------------------+
| date       | description        | ticker   |   qty |   proceeds |       ACB |   outlays |   capital gain/loss |
|------------+--------------------+----------+-------+------------+-----------+-----------+---------------------|
| 2023-07-15 | Partial Sell Apple | AAPL     |    60 |  14,257.41 | 12,130.99 |     13.17 |            2,113.26 |
| 2023-12-15 | Year End Rebalance | AAPL     |    40 |  10,702.40 |  8,087.33 |     13.36 |            2,601.71 |
+------------+--------------------+----------+-------+------------+-----------+-----------+---------------------+

GOOGL-2023
[Total Gains = 13,565.43]
+------------+---------------+----------+-------+------------+-----------+-----------+---------------------+
| date       | description   | ticker   |   qty |   proceeds |       ACB |   outlays |   capital gain/loss |
|------------+---------------+----------+-------+------------+-----------+-----------+---------------------|
| 2023-02-15 | Sell Tech     | GOOGL    |    15 |  52,302.90 | 46,200.25 |     13.40 |            6,089.25 |
| 2023-11-15 | Tech Profit   | GOOGL    |    10 |  38,290.00 | 30,800.17 |     13.66 |            7,476.17 |
+------------+---------------+----------+-------+------------+-----------+-----------+---------------------+
```
Your CSV file can contain transactions spanning across multiple different tickers. You can filter the above commands by running the following:
```bash
$ capgains calc tests/sample.csv 2023 -t AAPL
...

$ capgains show tests/sample.csv -t AAPL
...
```

To calculate the maximum cost of your foreign securities for T1135 reporting:
```bash
$ capgains maxcost tests/sample.csv 2023
AAPL-2023
[Max cost = 46,502.12]
[Year end = 26,283.81]

GOOGL-2023
[Max cost = 154,000.83]
[Year end = 77,000.41]

MSFT-2023
Nothing to report

RY.TO-2023
[Max cost = 31,732.48]
[Year end = 21,578.09]

SHOP.TO-2023
Nothing to report

TD.TO-2023
[Max cost = 24,341.65]
[Year end = 18,256.24]

VFV.TO-2023
[Max cost = 38,218.30]
[Year end = 33,441.02]
```

For additional commands and options, run one of the following:
```bash
$ capgains --help

$ capgains <command> --help
```
You can take this output and plug it into your favourite tax software (Simpletax, StudioTax, etc) and verify that the capital gains/losses that the tax software reports lines up with what the output of this command says.