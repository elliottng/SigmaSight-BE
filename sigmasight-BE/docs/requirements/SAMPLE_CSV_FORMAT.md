# Portfolio CSV Upload Format

## 1. Overview
This document defines the CSV format for uploading portfolio positions to SigmaSight. The format is designed to capture all essential position data while maintaining compatibility with common spreadsheet exports and the legacy Paragon Excel structure.

## 2. Required Columns

### 2.1 Core Position Data

#### 2.1.1 ticker - Security symbol (string)
- Stocks: Standard ticker (e.g., "AAPL", "MSFT")
- Options: OCC format (e.g., "AAPL240119C00150000")

#### 2.1.2 quantity - Number of shares or contracts (decimal)
- Positive for long positions
- Negative for short positions
- For options: number of contracts (1 contract = 100 shares)

#### 2.1.3 entry_price - Purchase/entry price per share (decimal)
- Always positive, even for shorts
- For options: price per contract

#### 2.1.4 entry_date - Date position was entered (date)
- Format: YYYY-MM-DD
- Used for cost basis and P&L calculations

#### 2.1.5 tags - Strategy/category tags (string)
- Comma-separated list
- Optional but recommended
- No spaces after commas

## 3. Optional Columns (Ignored but Accepted)
These columns may be present from Excel exports but will be calculated by the system:
- market_value
- exposure
- pnl
- weight
- any other columns

## 4. CSV Format Rules

### 4.1 General Requirements
- First row must contain column headers
- Column names are case-insensitive
- UTF-8 encoding required
- No blank rows within data
- Blank cells in optional columns are acceptable

### 4.2 Data Validation
- Ticker must be valid (system will verify)
- Quantity cannot be zero
- Entry price must be positive
- Entry date cannot be in future
- Entry date must be within last 5 years

## 5. Position Type Determination

### 5.1 Stocks
- LONG: quantity > 0
- SHORT: quantity < 0

### 5.2 Options (OCC Symbol Format)
Options use the standard OCC symbology: TICKERYYMMDDCSTRIKE

#### 5.2.1 Format Breakdown
- TICKER: Underlying symbol (variable length)
- YY: Year (2 digits)
- MM: Month (2 digits)
- DD: Day (2 digits)
- C/P: Call or Put (1 character)
- STRIKE: Strike price * 1000 (8 digits, including decimals)

#### 5.2.2 Position Types
- LC (Long Call): Call option with quantity > 0
- SC (Short Call): Call option with quantity < 0
- LP (Long Put): Put option with quantity > 0
- SP (Short Put): Put option with quantity < 0

## 6. Tag Guidelines

### 6.1 Recommended Tag Categories

#### 6.1.1 Strategy Tags
- momentum
- value
- growth
- hedge
- arbitrage
- pairs_trade
- income

#### 6.1.2 Sector Tags
- tech
- finance
- healthcare
- energy
- consumer
- industrial

#### 6.1.3 Risk Tags
- high_beta
- low_vol
- defensive
- cyclical

#### 6.1.4 Custom Tags
- Any alphanumeric string
- Use underscores for spaces
- Keep concise (max 20 characters)

## 7. Example CSV Files

### 7.1 Example 1: Mixed Portfolio
```csv
ticker,quantity,entry_price,entry_date,tags
AAPL,1000,150.00,2024-01-15,"momentum,tech"
MSFT,-500,380.00,2024-01-20,"hedge,tech"
JPM,800,140.50,2024-02-01,"value,finance"
TSLA,-200,195.00,2024-02-10,"hedge,high_beta"
AAPL240119C00150000,10,5.50,2024-01-10,"income,options"
SPY240119P00450000,5,8.25,2024-01-12,"hedge,options"
```

### 7.2 Example 2: Long/Short Equity
```csv
ticker,quantity,entry_price,entry_date,tags
NVDA,300,450.00,2024-01-05,"growth,tech,ai"
META,400,325.00,2024-01-08,"growth,tech"
XOM,1000,105.00,2024-01-10,"value,energy"
CVX,800,150.00,2024-01-10,"value,energy"
GME,-1000,18.50,2024-01-15,"short,meme"
AMC,-2000,5.25,2024-01-15,"short,meme"
RIVN,-500,19.00,2024-01-20,"short,ev"
```

### 7.3 Example 3: Options Strategy
```csv
ticker,quantity,entry_price,entry_date,tags
AAPL240119C00170000,20,3.50,2024-01-02,"bull_spread,long_leg"
AAPL240119C00180000,-20,1.50,2024-01-02,"bull_spread,short_leg"
MSFT240216P00350000,10,4.25,2024-01-05,"protection"
SPY240315C00470000,-5,2.75,2024-01-10,"income,covered_call"
```

## 8. Upload Process

### 8.1 File Size Limits
- Maximum 10MB per upload
- Maximum 10,000 positions per file

### 8.2 Processing
- Positions are validated row by row
- Invalid rows are reported but don't stop processing
- Duplicate positions (same ticker, same date) are rejected

### 8.3 Response
- Success: Number of positions created
- Errors: List of invalid rows with reasons
- Warnings: Data quality issues

## 9. Common Issues and Solutions

### 9.1 Date Format Errors
- Solution: Ensure dates are in YYYY-MM-DD format, not MM/DD/YYYY

### 9.2 Option Symbol Confusion
- Solution: Use exactly 8 digits for strike (e.g., 00150000 for $150.00)

### 9.3 Missing Tags
- Solution: Tags are optional; leave blank if not using

### 9.4 Negative Prices
- Solution: Entry price is always positive, even for shorts

### 9.5 Excel Number Formatting
- Solution: Remove currency symbols, thousand separators before export

## 10. Migration from Legacy Excel

### 10.1 Column Mapping
- symbol → ticker
- qty or quantity → quantity
- price → entry_price
- trade date → entry_date
- strategy → include in tags

### 10.2 Data Cleanup
- Remove thousand separators from numbers
- Convert date format to YYYY-MM-DD
- Combine multiple classification columns into tags

### 10.3 Calculated Fields
- Don't include mkt val, exposure, P&L
- System will calculate these automaticallyNo spaces after commas



Optional Columns (Ignored but Accepted)
These columns may be present from Excel exports but will be calculated by the system:

market_value
exposure
pnl
weight
any other columns

CSV Format Rules
General Requirements

First row must contain column headers
Column names are case-insensitive
UTF-8 encoding required
No blank rows within data
Blank cells in optional columns are acceptable

Data Validation

Ticker must be valid (system will verify)
Quantity cannot be zero
Entry price must be positive
Entry date cannot be in future
Entry date must be within last 5 years

Position Type Determination
The system automatically determines position type based on:
Stocks

LONG: quantity > 0
SHORT: quantity < 0

Options (OCC Symbol Format)
Options use the standard OCC symbology: TICKERYYMMDDCSTRIKE

TICKER: Underlying symbol (variable length)
YY: Year (2 digits)
MM: Month (2 digits)
DD: Day (2 digits)
C/P: Call or Put (1 character)
STRIKE: Strike price * 1000 (8 digits, including decimals)

Position types:

LC (Long Call): Call option with quantity > 0
SC (Short Call): Call option with quantity < 0
LP (Long Put): Put option with quantity > 0
SP (Short Put): Put option with quantity < 0

Tag Guidelines
Recommended Tag Categories
Strategy Tags:

momentum
value
growth
hedge
arbitrage
pairs_trade
income

Sector Tags:

tech
finance
healthcare
energy
consumer
industrial

Risk Tags:

high_beta
low_vol
defensive
cyclical

Custom Tags:

Any alphanumeric string
Use underscores for spaces
Keep concise (max 20 characters)

Example CSV Files
Example 1: Mixed Portfolio
csvticker,quantity,entry_price,entry_date,tags
AAPL,1000,150.00,2024-01-15,"momentum,tech"
MSFT,-500,380.00,2024-01-20,"hedge,tech"
JPM,800,140.50,2024-02-01,"value,finance"
TSLA,-200,195.00,2024-02-10,"hedge,high_beta"
AAPL240119C00150000,10,5.50,2024-01-10,"income,options"
SPY240119P00450000,5,8.25,2024-01-12,"hedge,options"
Example 2: Long/Short Equity
csvticker,quantity,entry_price,entry_date,tags
NVDA,300,450.00,2024-01-05,"growth,tech,ai"
META,400,325.00,2024-01-08,"growth,tech"
XOM,1000,105.00,2024-01-10,"value,energy"
CVX,800,150.00,2024-01-10,"value,energy"
GME,-1000,18.50,2024-01-15,"short,meme"
AMC,-2000,5.25,2024-01-15,"short,meme"
RIVN,-500,19.00,2024-01-20,"short,ev"
Example 3: Options Strategy
csvticker,quantity,entry_price,entry_date,tags
AAPL240119C00170000,20,3.50,2024-01-02,"bull_spread,long_leg"
AAPL240119C00180000,-20,1.50,2024-01-02,"bull_spread,short_leg"
MSFT240216P00350000,10,4.25,2024-01-05,"protection"
SPY240315C00470000,-5,2.75,2024-01-10,"income,covered_call"
Upload Process

File Size Limits

Maximum 10MB per upload
Maximum 10,000 positions per file


Processing

Positions are validated row by row
Invalid rows are reported but don't stop processing
Duplicate positions (same ticker, same date) are rejected


Response

Success: Number of positions created
Errors: List of invalid rows with reasons
Warnings: Data quality issues



Common Issues and Solutions
Issue: Date Format Errors
Solution: Ensure dates are in YYYY-MM-DD format, not MM/DD/YYYY
Issue: Option Symbol Confusion
Solution: Use exactly 8 digits for strike (e.g., 00150000 for $150.00)
Issue: Missing Tags
Solution: Tags are optional; leave blank if not using
Issue: Negative Prices
Solution: Entry price is always positive, even for shorts
Issue: Excel Number Formatting
Solution: Remove currency symbols, thousand separators before export
Migration from Legacy Excel
If migrating from Paragon Excel files:

Column Mapping:

symbol → ticker
qty or quantity → quantity
price → entry_price
trade date → entry_date
strategy → include in tags


Data Cleanup:

Remove thousand separators from numbers
Convert date format to YYYY-MM-DD
Combine multiple classification columns into tags


Calculated Fields:

Don't include mkt val, exposure, P&L
System will calculate these automatically