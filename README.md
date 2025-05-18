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
Here is a sample CSV file:
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
$ capgains show sample.csv
+------------+---------------+----------+----------+-------+---------+--------------+------------+
| date       | description   | ticker   | action   |   qty |   price |   commission |   currency |
|------------+---------------+----------+----------+-------+---------+--------------+------------|
| 2017-02-15 | ESPP PURCHASE | GOOG     | BUY      |   100 |   50.00 |        10.00 |        USD |
| 2017-05-20 | RSU VEST      | GOOG     | SELL     |    50 |   45.00 |         0.00 |        CAD |
+------------+---------------+----------+----------+-------+---------+--------------+------------+
```
To calculate the capital gains you can run:
```bash
$ capgains calc sample.csv 2017
GOOG-2017
[Total Gains = -1,028.54]
+------------+---------------+----------+-------+------------+----------+-----------+---------------------+
| date       | description   | ticker   | qty   |   proceeds |      ACB |   outlays |   capital gain/loss |
|------------+---------------+----------+-------+------------+----------+-----------+---------------------|
| 2017-05-20 | RSU VEST      | GOOG     | 50    |   2,250.00 | 3,278.54 |      0.00 |           -1,028.54 |
+------------+---------------+----------+-------+------------+----------+-----------+---------------------+
```
Your CSV file can contain transactions spanning across multiple different tickers. You can filter the above commands by running the following:
```bash
$ capgains calc sample.csv 2017 -t GOOG
...

$ capgains show sample.csv -t GOOG
...
```

To calculate the maximum cost of your foreign securities for T1135 reporting:
```bash
$ capgains maxcost sample.csv 2023
GOOG-2023 Maximum Cost
+------------+-----------+------------+
| ticker     | currency  | max cost   |
|------------+-----------+------------|
| GOOG       | USD      | 5,010.00   |
+------------+-----------+------------+
Maximum cost in CAD: 6,762.51
```

For additional commands and options, run one of the following:
```bash
$ capgains --help

$ capgains <command> --help
```
You can take this output and plug it into your favourite tax software (Simpletax, StudioTax, etc) and verify that the capital gains/losses that the tax software reports lines up with what the output of this command says.