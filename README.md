# Canadian Capital Gains CLI Tool

[![Build Status](https://travis-ci.org/EmilMaric/cad-capital-gains.svg?branch=master)](https://travis-ci.org/EmilMaric/cad-capital-gains)
[![codecov](https://codecov.io/gh/EmilMaric/cad-capital-gains/branch/master/graph/badge.svg)](https://codecov.io/gh/EmilMaric/cad-capital-gains)

⚠️ **IMPORTANT LEGAL NOTICE**: This software is provided "as is" without any warranties. By using this software, you agree to the terms outlined in [LEGAL.md](LEGAL.md). Users MUST read and agree to these terms before using the software.

## Overview
Calculating your capital gains and tracking your adjusted cost base (ACB) manually, or using an Excel document, often proves to be a laborious process. This CLI tool calculates your capital gains and ACB for you, and just requires a transaction file (CSV or JSON) with basic information about your transactions. The idea with this tool is that you are able to more or less cut-and-copy the output that it generates and copy it into whatever tax filing software you end up using.

⚠️ **IMPORTANT**: This tool only supports full superficial capital losses, and does not support partial superficial losses. Please ensure you understand this limitation before using the tool for tax purposes.

## Features
- Calculate capital gains for stocks traded in both CAD and USD
- Track adjusted cost base (ACB) across multiple years
- Support for both CSV and JSON input formats
- Handle superficial loss rules automatically
- Calculate maximum cost for T1135 reporting
- Support for both table and JSON output formats
- Alert you if your holdings exceed the T1135 reporting threshold
- Break down the maximum cost by ticker for detailed reporting
- Support transactions with multiple different stock tickers in the same file
- Automatically fetch daily exchange rates from the Bank of Canada for USD transactions
- Apply [superficial capital loss](https://www.canada.ca/en/revenue-agency/services/tax/individuals/topics/about-your-tax-return/tax-return/completing-a-tax-return/personal-income/line-127-capital-gains/capital-losses-deductions/what-a-superficial-loss.html) rules when calculating gains and ACB
  - Only supports full superficial capital losses (not partial)
  - Losses are carried forward as prescribed by the CRA
  - A sale with a capital loss will be treated as superficial if:
    - Shares with the same ticker were bought in the 61 day window (30 days before or 30 days after the sale)
    - There is a non-zero balance of shares sharing the same ticker at the end of the 61 day window
- Support fractional quantities of shares

### Important Notes
- The tool uses the Bank of Canada's noon rates (pre-2017) and indicative rates (post-2017) for currency conversion
- Maximum cost is calculated based on the adjusted cost base (ACB) of your holdings
- The tool considers both buying and selling activities throughout the year
- If your maximum cost exceeds CAD $100,000, ensure you file form T1135 with your tax return to avoid penalties

## T1135 Foreign Income Verification Statement
The T1135 form is a requirement from the Canada Revenue Agency (CRA) for Canadian residents who own specified foreign property with a total cost of more than CAD $100,000 at any time during the tax year. This includes foreign securities held in Canadian brokerage accounts.

### When is T1135 Required?
You must file a T1135 if:
- You are a Canadian resident for tax purposes
- You owned specified foreign property (including foreign stocks) with a total cost exceeding CAD $100,000 at any time during the year
- The securities are held for investment purposes (not personal use)

### How This Tool Helps with T1135
This tool provides the `maxcost` command to help with T1135 reporting. To calculate the maximum cost of your foreign securities for T1135 reporting:

```bash
$ capgains maxcost tests/sample.csv 2023
```
or
```bash
$ capgains maxcost tests/sample.json 2023
```


This command will:
- Calculate the maximum cost of your foreign securities during the tax year
- Show the maximum cost in CAD using official Bank of Canada exchange rates
- Break down the costs by individual security
- Alert you if you exceed the T1135 reporting threshold

# Installation and Setup

## Quick Install
```bash
# To get the latest release
pip install cad-capgains
```

## Try it with Sample Data
The package includes comprehensive sample datasets in both CSV (`tests/sample.csv`) and JSON (`tests/sample.json`) formats that you can use to try out the tool. After installation, you can run:
```bash
# Show all transactions (using CSV)
capgains show tests/sample.csv

# Show specific stock transactions (using JSON)
capgains show tests/sample.json -t AAPL

# Calculate capital gains for 2023
capgains calc tests/sample.csv 2023

# Check maximum cost for T1135 reporting
capgains maxcost tests/sample.json 2023
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

# Input File Requirements
The tool supports both CSV and JSON input formats for transaction data.

## CSV Format
Create a CSV file with each line representing a `BUY` or `SELL` transaction. Transactions **must be in chronological order**. The format is:
```csv
<yyyy-mm-dd>,<description>,<stock_ticker>,<action(BUY/SELL)>,<quantity>,<price>,<commission>,<currency>
```

Example:
```csv
2017-2-15,ESPP PURCHASE,GOOG,BUY,100,50.00,10.00,USD
2017-5-20,RSU VEST,GOOG,SELL,50,45.00,0.00,CAD
```

## JSON Format
Create a JSON file containing an array of transaction objects. Transactions **must be in chronological order**. The format is:
```json
[
  {
    "date": "2017-02-15",
    "description": "ESPP PURCHASE",
    "ticker": "GOOG",
    "action": "BUY",
    "qty": 100,
    "price": 50.00,
    "commission": 10.00,
    "currency": "USD"
  },
  {
    "date": "2017-05-20",
    "description": "RSU VEST",
    "ticker": "GOOG",
    "action": "SELL",
    "qty": 50,
    "price": 45.00,
    "commission": 0.00,
    "currency": "CAD"
  }
]
```

**NOTE: This tool only supports calculating ACB and capital gains with transactions
dating from May 1, 2007 and onwards.**

# Usage
To show the transaction file in a nice tabular format you can run:
```bash
$ capgains show tests/sample.csv
+------------+--------------------+----------+----------+-------+----------+--------------+------------+
| date       | description        | ticker   | action   |   qty |    price |   commission |   currency |
|------------+--------------------+----------+----------+-------+----------+--------------+------------|
| 2022-01-15 | Initial Purchase   | AAPL     | BUY      |   100 |   142.50 |         9.99 |        USD |
| 2022-02-10 | Buy Canadian Bank  | TD.TO    | BUY      |   150 |    78.25 |         9.99 |        CAD |
| 2022-03-20 | Buy Tech           | GOOGL    | BUY      |    20 | 2,200.00 |         9.99 |        USD |
...
```

You can also output the results in JSON format:
```bash
$ capgains show tests/sample.csv --format json
{
  "transactions": [
    {
      "date": "2022-01-15",
      "description": "Initial Purchase",
      "ticker": "AAPL",
      "action": "BUY",
      "quantity": 100,
      "price": 142.50,
      "commission": 9.99,
      "currency": "USD"
    },
    ...
  ]
}
```