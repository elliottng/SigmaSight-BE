# SigmaSight User Guide

**Welcome to SigmaSight - Institutional Grade Portfolio Risk Management**

**Version**: 1.0  
**Last Updated**: August 26, 2025  
**Application URL**: http://localhost:3008  

## Table of Contents

1. [Getting Started](#getting-started)
2. [Dashboard Overview](#dashboard-overview)
3. [AI Chat Interface](#ai-chat-interface)
4. [Portfolio Analytics](#portfolio-analytics)
5. [Risk Management](#risk-management)
6. [Position Management](#position-management)
7. [Reports and Exports](#reports-and-exports)
8. [Advanced Features](#advanced-features)
9. [Troubleshooting](#troubleshooting)

---

## Getting Started

### System Requirements

**Recommended Browser**: Chrome 90+, Firefox 90+, Safari 14+, Edge 90+
**Internet Connection**: Required for real-time data and AI features
**Screen Resolution**: 1024x768 minimum, 1920x1080 recommended

### Accessing SigmaSight

1. **Open your web browser**
2. **Navigate to**: http://localhost:3008
3. **You should see**: SigmaSight dashboard with portfolio overview

*Note: No login required for demo mode - you'll have immediate access to three demo portfolios*

### Demo Portfolios Available

SigmaSight includes three fully-configured demo portfolios:

#### 1. Individual Investor Portfolio
- **Type**: Balanced retail investor portfolio
- **Assets**: 16 diversified positions
- **Strategy**: Long-term growth with moderate risk
- **Typical Holdings**: Blue-chip stocks, ETFs, bonds
- **Risk Level**: Moderate

#### 2. High Net Worth Portfolio  
- **Type**: Sophisticated investor portfolio
- **Assets**: 17 advanced positions
- **Strategy**: Alternative investments and tax optimization
- **Typical Holdings**: Private equity, REITs, international exposure
- **Risk Level**: Moderate to High

#### 3. Hedge Fund Style Portfolio
- **Type**: Long/short equity strategy
- **Assets**: 30 positions including options
- **Strategy**: Market-neutral with leverage
- **Typical Holdings**: Long/short equity pairs, options, derivatives
- **Risk Level**: High

### First Time Setup

When you first access SigmaSight:

1. **Dashboard loads automatically** with portfolio overview
2. **All demo data is pre-loaded** - no configuration needed
3. **Real-time calculations** are ready immediately
4. **AI chat interface** is available for instant analysis

---

## Dashboard Overview

The main dashboard provides a comprehensive view of your portfolio performance and risk metrics.

### Key Components

#### 1. Portfolio Summary Cards

**Total Portfolio Value**
- Current market value of all positions
- Daily change in absolute dollars and percentage
- Visual indicators for positive/negative performance

**Risk Metrics**
- Value at Risk (VaR) at 99% confidence level
- Expected Shortfall (ES) for tail risk
- Portfolio volatility and beta measures

**Exposure Analysis**
- Gross exposure (sum of absolute position values)
- Net exposure (long positions minus short positions)
- Leverage ratio and concentration metrics

#### 2. Performance Charts

**Portfolio Timeline**
- Historical value progression
- Daily P&L visualization
- Benchmark comparison (when available)

**Risk Decomposition**
- Factor contribution charts
- Sector/industry breakdown
- Position-level risk attribution

#### 3. Alerts Panel

**Risk Alerts**
- High concentration warnings
- Options expiration notices
- Limit breach notifications

**Opportunities**
- Rebalancing suggestions
- Hedge recommendations
- Market timing insights

### Navigation Menu

**Main Sections**:
- **Dashboard** - Overview and key metrics
- **Chat** - AI-powered portfolio analysis
- **Positions** - Detailed position management
- **Risk** - Advanced risk analytics
- **Market** - Real-time market data
- **Reports** - Generated portfolio reports

### Quick Actions

**From Dashboard**:
- Click any metric card for detailed analysis
- Use the chat button for AI insights
- Access reports via the Reports menu
- View individual positions in the Positions tab

---

## AI Chat Interface

The AI Chat interface is SigmaSight's flagship feature, providing natural language access to sophisticated portfolio analysis.

### Accessing Chat

**Method 1**: Click the "Chat" tab in the main navigation
**Method 2**: Click the AI chat icon in the top navigation bar
**Method 3**: Navigate directly to http://localhost:3008/chat

### How to Use the Chat Interface

#### Starting a Conversation

1. **Type your question** in the text input field at the bottom
2. **Press Enter** or click the send button
3. **Wait for AI analysis** - typically 2-5 seconds
4. **Review the detailed response** with insights and recommendations

#### Example Queries

**Risk Analysis**:
- "What are my biggest risks today?"
- "How concentrated is my portfolio?"
- "What's my exposure to the tech sector?"
- "Show me my options that expire this week"

**Performance Questions**:
- "What's driving my portfolio performance?"
- "Which positions are my best performers?"
- "How am I performing vs the market?"
- "What caused my recent gains/losses?"

**Factor Analysis**:
- "What's my exposure to value vs growth stocks?"
- "How is my portfolio positioned for rising rates?"
- "Am I tilted toward small cap or large cap?"
- "What are my factor exposures?"

**Recommendations**:
- "Should I rebalance my portfolio?"
- "What hedges would you recommend?"
- "How can I reduce my risk?"
- "What sectors should I consider adding?"

#### Understanding AI Responses

**Response Structure**:
1. **Executive Summary** - Key findings in plain English
2. **Detailed Analysis** - Specific metrics and data points
3. **Recommendations** - Actionable next steps
4. **Risk Warnings** - Important considerations

**Data Sources**:
- All analysis is based on **real portfolio calculations**
- AI interprets backend analytics, never estimates values
- **Current data** as of the latest calculation run
- **Gap identification** when data is unavailable

#### Advanced Chat Features

**Context Awareness**:
- Chat remembers your conversation history
- Asks clarifying questions when needed
- Understands follow-up questions
- Maintains portfolio context throughout

**Multi-Format Responses**:
- Plain English explanations
- Structured data when requested
- Bullet point summaries
- Numerical analysis with context

### Chat Best Practices

**For Best Results**:
1. **Be specific** about what you want to analyze
2. **Ask follow-up questions** to drill deeper
3. **Request explanations** of complex concepts
4. **Use natural language** - no special syntax needed

**Example Conversation Flow**:
```
User: "What are my biggest risks?"

AI: "I've identified three primary risks in your portfolio:

1. **Sector Concentration**: 35% exposure to technology sector
   - Above typical 25% diversification threshold
   - Creates vulnerability to tech-specific events

2. **Options Gamma Risk**: High gamma exposure expiring Friday
   - 850 delta equivalent in expiring options
   - Could cause significant position changes

3. **Market Beta**: Portfolio beta of 1.25
   - Higher volatility than broad market
   - Amplifies both gains and losses

Recommendations:
- Reduce tech allocation to <30%
- Consider rolling expiring options
- Add defensive positions to lower beta"

User: "How should I reduce tech exposure?"

AI: "Here are three strategies to reduce your tech concentration:

1. **Trim Largest Positions**: 
   - Reduce AAPL by 25% (from $50k to $37.5k)
   - Trim MSFT by 20% (from $40k to $32k)
   - This alone reduces tech exposure by 8%

2. **Add Non-Tech Positions**:
   - Consider healthcare (XLV) or utilities (XLU)
   - Target 5-10% allocation each
   - Provides defensive characteristics

3. **Sector Rotation ETFs**:
   - Use XLK (tech) to XLF (financial) pair trade
   - Maintains market exposure while reducing sector risk
   - Can implement gradually over 2-3 weeks

Would you like specific position sizes for any of these strategies?"
```

---

## Portfolio Analytics

### Portfolio Summary

**Accessing**: Dashboard → Portfolio Overview Cards

**Key Metrics**:

**Valuation Metrics**:
- **Market Value**: Current total portfolio value
- **Cost Basis**: Original investment amounts
- **Unrealized P&L**: Gains/losses not yet realized
- **Daily Change**: 24-hour value change

**Risk Metrics**:
- **Volatility**: Annualized portfolio standard deviation
- **Beta**: Market sensitivity (vs S&P 500)
- **Sharpe Ratio**: Risk-adjusted returns
- **Maximum Drawdown**: Largest peak-to-trough decline

**Exposure Metrics**:
- **Gross Exposure**: Sum of absolute position values
- **Net Exposure**: Long positions minus short positions  
- **Long Exposure**: Total value of long positions
- **Short Exposure**: Total value of short positions

### Performance Analysis

**Time Period Analysis**:
- **Daily**: Last trading day performance
- **Weekly**: 7-day performance
- **Monthly**: 30-day performance
- **Year-to-Date**: Performance since January 1st

**Attribution Analysis**:
- **Security Attribution**: Performance by individual position
- **Sector Attribution**: Performance by sector/industry
- **Style Attribution**: Performance by investment style factors

**Benchmark Comparison**:
- **Relative Performance**: Portfolio vs benchmarks
- **Tracking Error**: Standard deviation of relative returns
- **Information Ratio**: Risk-adjusted relative performance

### Factor Exposure Analysis

SigmaSight uses a comprehensive 7-factor model:

#### Core Factors

**1. Market Beta**
- Measures sensitivity to overall market movements
- Beta > 1: More volatile than market
- Beta < 1: Less volatile than market

**2. Value Factor**
- Exposure to undervalued stocks
- High value: Preference for low P/E, P/B ratios
- Low value: Growth-oriented positions

**3. Growth Factor** 
- Exposure to high-growth companies
- High growth: Companies with strong earnings growth
- Low growth: Mature, stable companies

**4. Momentum Factor**
- Exposure to recently outperforming stocks
- High momentum: Stocks with strong recent returns
- Low momentum: Recently underperforming stocks

**5. Quality Factor**
- Exposure to financially strong companies
- High quality: Strong balance sheets, stable earnings
- Low quality: Higher financial risk

**6. Size Factor**
- Exposure to small vs large cap stocks
- Positive: Small cap tilt
- Negative: Large cap tilt

**7. Low Volatility Factor**
- Exposure to low-volatility stocks
- High exposure: Preference for stable stocks
- Low exposure: Acceptance of higher volatility

#### Reading Factor Exposures

**Factor Exposure Scale**:
- **+1.0**: Very high positive exposure
- **+0.5**: Moderate positive exposure
- **0.0**: Neutral exposure
- **-0.5**: Moderate negative exposure
- **-1.0**: Very high negative exposure

**Example Interpretation**:
```
Market Beta: 1.15    (15% more volatile than market)
Value: -0.25         (Slight growth tilt)
Growth: 0.45         (Moderate growth exposure)
Momentum: 0.10       (Slight momentum tilt)
Quality: 0.30        (Preference for quality companies)
Size: -0.15          (Slight large-cap tilt)
Low Vol: -0.20       (Accepting higher volatility)
```

### Sector and Industry Analysis

**Sector Breakdown**:
- Technology, Healthcare, Financial Services
- Consumer Discretionary, Consumer Staples
- Industrials, Materials, Energy
- Utilities, Real Estate, Communications

**Industry Analysis**:
- Detailed industry classifications within sectors
- Concentration analysis by industry
- Industry-specific risk metrics

**Geographic Exposure**:
- Domestic vs International allocation
- Developed vs Emerging market exposure
- Currency exposure analysis

---

## Risk Management

### Value at Risk (VaR) Analysis

**What is VaR?**
Value at Risk estimates the maximum potential loss over a specific time period at a given confidence level.

**VaR Metrics in SigmaSight**:
- **1-Day VaR (99%)**: Maximum expected loss in 1 day, 99% confidence
- **1-Week VaR (95%)**: Maximum expected loss in 1 week, 95% confidence
- **1-Month VaR (95%)**: Maximum expected loss in 1 month, 95% confidence

**Reading VaR Numbers**:
- **VaR of -$10,000 (99%, 1-day)**: In 99% of cases, daily losses won't exceed $10,000
- **Only 1% chance** of losing more than the VaR amount
- **Not a maximum possible loss** - just a statistical confidence level

### Expected Shortfall (ES)

**What is Expected Shortfall?**
ES estimates the average loss when losses exceed the VaR threshold.

**Why ES Matters**:
- **Tail Risk Measure**: Shows severity of worst-case scenarios
- **Beyond VaR**: Captures losses in the worst 1% of cases
- **Risk Budgeting**: Helps size positions for extreme events

**Example**:
```
VaR (99%, 1-day): -$15,000
ES (99%, 1-day): -$22,000

Interpretation:
- 99% of days, losses stay below $15,000
- In the worst 1% of days, average loss is $22,000
- Helps understand tail risk exposure
```

### Stress Testing

**Predefined Scenarios**:
- **Market Crash**: -20% equity market decline
- **Rate Shock**: +200 basis point rate increase
- **Credit Crisis**: Credit spread widening
- **Volatility Spike**: VIX increase to 40+
- **Currency Crisis**: Major currency movements

**Custom Scenarios**:
- **Sector Rotation**: Specific sector declines
- **Stock-Specific Events**: Individual position shocks
- **Correlation Breakdown**: Diversification failure
- **Liquidity Crisis**: Bid-ask spread widening

**Interpreting Stress Tests**:
- **Scenario P&L**: Expected gain/loss in each scenario
- **Worst Case**: Most severe potential outcome
- **Best Case**: Most favorable potential outcome
- **Probability Weighted**: Expected outcome across all scenarios

### Options Risk Management

**Greeks Overview**:

**Delta**
- **Measures**: Price sensitivity to underlying stock movement
- **Portfolio Delta**: Net exposure to underlying price moves
- **Management**: High delta = high directional risk

**Gamma**  
- **Measures**: Rate of change of delta
- **Portfolio Gamma**: Acceleration of P&L changes
- **Management**: High gamma = position changes rapidly

**Theta**
- **Measures**: Time decay of option values
- **Portfolio Theta**: Daily time decay P&L
- **Management**: Negative theta = losing money over time

**Vega**
- **Measures**: Sensitivity to implied volatility changes
- **Portfolio Vega**: Exposure to volatility risk
- **Management**: High vega = volatility sensitive

**Example Greeks Analysis**:
```
Portfolio Greeks Summary:
Delta: +$125,000    (Bullish directional exposure)
Gamma: -$8,500      (Short gamma = short acceleration)
Theta: -$450/day    (Losing $450 daily to time decay)
Vega: +$12,000      (Long volatility exposure)

Risk Assessment:
- Strong bullish bias (high positive delta)
- Short gamma creates risk in volatile markets
- Time decay working against the portfolio
- Benefits from volatility increases
```

### Risk Limits and Alerts

**Automatic Alerts**:
- **Concentration Risk**: Single position >10% of portfolio
- **Sector Risk**: Sector allocation >25% of portfolio
- **VaR Breach**: Daily VaR exceeds preset limits
- **Options Expiration**: Options expiring within 5 days
- **Correlation Risk**: Portfolio correlation above 0.8

**Risk Budgeting**:
- **Position Size Limits**: Maximum allocation per position
- **Sector Limits**: Maximum allocation per sector
- **Geographic Limits**: Domestic vs international limits
- **Volatility Budgets**: Maximum portfolio volatility targets

---

## Position Management

### Position Overview Table

**Accessing**: Navigate to Positions tab

**Column Descriptions**:

**Basic Information**:
- **Symbol**: Ticker symbol or option identifier
- **Name**: Full company or security name
- **Type**: LONG, SHORT, LC (Long Call), LP (Long Put), SC (Short Call), SP (Short Put)
- **Quantity**: Number of shares or contracts

**Valuation**:
- **Price**: Current market price per share/contract
- **Market Value**: Current total position value (Price × Quantity)
- **Cost Basis**: Original purchase price
- **Unrealized P&L**: Current gain/loss vs cost basis
- **% Return**: Percentage return since purchase

**Risk Metrics**:
- **Beta**: Individual position beta vs market
- **Volatility**: Annualized volatility of the position
- **Risk Contribution**: Contribution to total portfolio risk
- **Correlation**: Average correlation with other positions

**Options-Specific** (for options positions):
- **Strike**: Strike price of the option
- **Expiration**: Expiration date
- **Days to Expiry**: Calendar days until expiration
- **Delta/Gamma/Theta/Vega**: Individual Greeks

### Position Actions

**Available Actions**:
- **View Details**: Click any row for detailed position analysis
- **Edit Position**: Modify quantity, price, or other attributes
- **Add Tags**: Categorize positions with custom tags
- **Close Position**: Remove position from portfolio
- **Clone Position**: Create similar position with different parameters

### Position Filtering and Sorting

**Filter Options**:
- **Position Type**: Filter by LONG, SHORT, options types
- **Sector/Industry**: Show only specific sectors
- **Tags**: Filter by custom tags
- **P&L Status**: Show only profitable or losing positions
- **Expiration**: Filter options by expiration date

**Sorting Options**:
- **Market Value**: Largest to smallest positions
- **P&L**: Best to worst performers
- **Risk Contribution**: Highest to lowest risk
- **Expiration Date**: Earliest to latest expiring options

### Position Details View

**Detailed Analysis**:
- **Price History**: Historical price chart
- **Performance Attribution**: What drove returns
- **Factor Exposures**: How position fits in factor model
- **Correlations**: Relationships with other positions
- **Risk Metrics**: Comprehensive risk analysis

**Options Analysis** (for options positions):
- **Greeks Over Time**: How Greeks change with time/price
- **Breakeven Analysis**: Profit/loss at different underlying prices
- **Implied Volatility**: Current IV vs historical levels
- **Time Decay**: How position value changes over time

### Portfolio Construction Tools

**Adding New Positions**:
1. Click "Add Position" button
2. Enter symbol, quantity, price
3. Select position type (LONG/SHORT/Options)
4. Add tags and notes
5. Save position

**Position Sizing Guidance**:
- **Risk-Based Sizing**: Size based on position volatility
- **Factor Neutral**: Size to maintain factor neutrality
- **Concentration Limits**: Respect position size limits
- **Correlation Adjusted**: Consider correlations with existing positions

**Rebalancing Tools**:
- **Target Weights**: Set target allocation percentages
- **Rebalance Calculator**: Calculate trades needed for targets
- **Tax Optimization**: Consider tax implications of trades
- **Trading Cost Analysis**: Estimate costs of rebalancing

---

## Reports and Exports

### Available Report Types

SigmaSight generates comprehensive reports in multiple formats:

#### 1. JSON Reports
**Purpose**: Structured data for API consumption or custom analysis
**Contains**:
- Complete portfolio snapshot with all positions
- Calculated metrics and risk measures
- Factor exposures and correlations
- Historical performance data

**Use Cases**:
- API integration with other systems
- Custom analysis in Excel or Python
- Data warehouse loading
- Backup and archival

#### 2. CSV Reports  
**Purpose**: Tabular data for spreadsheet analysis
**Contains**:
- Position-level data in rows
- All metrics in separate columns
- Easy sorting and filtering
- Compatible with Excel, Google Sheets

**Use Cases**:
- Excel pivot table analysis
- Database imports
- Client reporting templates
- Performance tracking

#### 3. Markdown Reports
**Purpose**: Human-readable documentation
**Contains**:
- Executive summary of portfolio
- Key insights and findings
- Risk analysis and recommendations
- Formatted for easy reading

**Use Cases**:
- Client presentations
- Investment committee reports
- Documentation and archival
- Email summaries

### Accessing Reports

**Method 1: Reports Tab**
1. Navigate to Reports in main menu
2. Select desired portfolio
3. Choose report format (JSON/CSV/MD)
4. Click "View Report" or "Download"

**Method 2: Dashboard Quick Access**
1. From any portfolio view
2. Click "Generate Report" button
3. Select format and options
4. Report opens in new tab/downloads

### Report Contents

#### Executive Summary Section
- **Portfolio Overview**: Total value, P&L, key metrics
- **Risk Assessment**: VaR, stress test results, major risks
- **Performance**: Returns vs benchmarks, attribution
- **Recommendations**: Key action items and insights

#### Detailed Analysis Sections

**Position Analysis**:
- Complete position listing with all metrics
- Performance attribution by position
- Risk contribution analysis
- Options Greeks summary (if applicable)

**Factor Analysis**:
- 7-factor model exposures
- Factor performance attribution
- Sector and style analysis
- Geographic and currency exposures

**Risk Analysis**:
- VaR and Expected Shortfall calculations
- Stress testing results across scenarios
- Correlation analysis and concentration metrics
- Options risk analysis (Greeks, time decay)

**Performance Analysis**:
- Historical returns and volatility
- Benchmark comparisons
- Risk-adjusted performance metrics
- Monthly/quarterly performance breakdown

#### Technical Appendix
- Calculation methodologies
- Data sources and timestamps
- Assumptions and limitations
- Model descriptions and parameters

### Custom Report Options

**Date Range Selection**:
- Daily snapshot reports
- Weekly/monthly summaries
- Custom date ranges
- Historical report comparison

**Content Customization**:
- Include/exclude specific sections
- Focus on particular asset classes
- Filter by position types or sectors
- Add custom commentary fields

**Formatting Options**:
- Logo and branding customization
- Color schemes and styling
- Page layouts and section ordering
- Chart and visualization preferences

### Automated Report Generation

**Scheduled Reports**:
- Daily portfolio summaries
- Weekly risk reports
- Monthly performance reports
- Quarterly comprehensive reviews

**Delivery Options**:
- Email distribution lists
- FTP/SFTP file delivery
- API push to other systems
- Cloud storage integration

**Alert-Triggered Reports**:
- Risk limit breach reports
- Performance milestone reports
- Significant position change reports
- Market event impact reports

### Report Sharing and Collaboration

**Internal Sharing**:
- Team member access controls
- Comment and annotation features
- Version tracking and history
- Approval workflow integration

**Client Delivery**:
- Password-protected reports
- Branded client portals
- White-label customization
- Compliance-approved templates

**Regulatory Reporting**:
- Standardized formats for regulators
- Audit trail maintenance
- Data integrity verification
- Retention policy compliance

---

## Advanced Features

### What-If Scenario Analysis

**Accessing**: Navigate to Risk → Scenarios or use Chat interface

**Types of Analysis**:

#### 1. Position Changes
**Add/Remove Positions**:
- Model impact of new position additions
- Analyze effect of closing existing positions
- Compare multiple position change scenarios
- Optimize position sizing for risk/return

**Example Usage**:
```
Chat: "What if I add $50k of SPY?"

AI Response: "Adding $50k SPY position would:
- Increase gross exposure by 4.2%
- Reduce portfolio beta from 1.15 to 1.12
- Lower concentration risk (largest position drops to 8.5%)
- Increase diversification (correlation drops from 0.65 to 0.61)
- Expected tracking error vs benchmark decreases 15%

Recommendation: Positive diversification impact with moderate beta reduction"
```

#### 2. Market Scenarios
**Predefined Scenarios**:
- Market up/down 5%, 10%, 20%
- Interest rate changes +/-100bp, +/-200bp
- Volatility regime changes (VIX 15 vs 30 vs 45)
- Sector rotation scenarios
- Currency movement impacts

**Custom Scenarios**:
- Specific stock price changes
- Earnings announcement impacts
- Geopolitical event modeling
- Seasonal effect analysis

#### 3. Time-Based Analysis
**Options Time Decay**:
- Portfolio value after 1 week, 1 month, 3 months
- Impact of time decay on options positions
- Expiration scenario analysis
- Roll-forward strategy comparison

**Performance Projections**:
- Expected portfolio evolution under different conditions
- Rebalancing schedule optimization
- Tax harvesting opportunity analysis
- Cash flow impact modeling

### Advanced Risk Analytics

#### 1. Correlation Analysis

**Pairwise Correlations**:
- Correlation matrix for all positions
- Rolling correlation analysis
- Correlation clustering and grouping
- Diversification benefit analysis

**Dynamic Correlation**:
- How correlations change during stress periods
- Crisis correlation vs normal correlation
- Portfolio concentration during tail events
- Diversification breakdown analysis

#### 2. Attribution Analysis

**Performance Attribution**:
- Security selection vs allocation effects
- Factor attribution (style, sector, country)
- Active vs passive return components
- Risk attribution vs return attribution

**Risk Attribution**:
- Which positions contribute most to portfolio risk
- Factor risk contribution breakdown
- Concentration risk vs diversification benefit
- Options risk vs underlying equity risk

#### 3. Liquidity Analysis

**Position Liquidity**:
- Average daily volume vs position size
- Days-to-liquidate analysis
- Bid-ask spread impact
- Market impact cost estimates

**Portfolio Liquidity**:
- Weighted average liquidity metrics
- Liquidity-at-risk calculations
- Funding liquidity analysis
- Stress scenario liquidity needs

### Optimization Features

#### 1. Risk Optimization

**Risk Parity**:
- Equal risk contribution optimization
- Factor risk balancing
- Volatility targeting
- Maximum diversification optimization

**Minimum Variance**:
- Lowest risk portfolio for given constraints
- Risk budgeting optimization
- Tracking error minimization
- Downside risk minimization

#### 2. Return Optimization

**Mean Variance Optimization**:
- Efficient frontier construction
- Expected return maximization for risk level
- Sharpe ratio optimization
- Information ratio maximization

**Factor-Based Optimization**:
- Factor exposure targeting
- Smart beta optimization
- ESG score optimization
- Dividend yield optimization

#### 3. Constraint Handling

**Position Constraints**:
- Minimum/maximum position sizes
- Sector allocation constraints
- Turnover constraints
- Transaction cost constraints

**Risk Constraints**:
- Maximum portfolio volatility
- VaR limits and constraints
- Tracking error constraints
- Factor exposure limits

### Integration Features

#### 1. Data Connectivity

**Market Data**:
- Real-time price feeds
- Historical data backfill
- Corporate actions processing
- Earnings and event calendars

**External Systems**:
- Portfolio management systems
- Order management systems
- Risk management platforms
- Reporting and client systems

#### 2. API Access

**RESTful APIs**:
- Portfolio data retrieval
- Position management
- Risk calculations
- Report generation

**WebSocket Feeds**:
- Real-time portfolio updates
- Price change notifications
- Risk alert streaming
- Performance monitoring

#### 3. Custom Analytics

**Python Integration**:
- Custom calculation scripts
- Advanced statistical analysis
- Machine learning model integration
- Backtesting framework

**R Integration**:
- Statistical modeling
- Risk model development
- Performance analysis
- Visualization tools

---

## Troubleshooting

### Common Issues

#### 1. Application Not Loading

**Symptoms**:
- Blank page or loading spinner that doesn't complete
- Browser shows "This site can't be reached"
- Error message about connection refused

**Solutions**:
```bash
1. Verify all services are running:
   - Backend: http://localhost:8001/docs should show API docs
   - Frontend: http://localhost:3008 should load application
   - GPT Agent: http://localhost:8888/health should return OK

2. Check service startup:
   - Backend: cd backend && uv run python run.py
   - Frontend: cd frontend && npm run dev
   - GPT Agent: cd gptagent && npm run dev

3. Clear browser cache:
   - Hard refresh: Ctrl+F5 (Windows) or Cmd+Shift+R (Mac)
   - Clear browser cache and cookies
   - Try incognito/private browsing mode
```

#### 2. Data Not Loading

**Symptoms**:
- Dashboard shows "No data available"
- Empty portfolio or position lists
- Charts not displaying

**Solutions**:
```bash
1. Check database connection:
   - Verify PostgreSQL is running
   - Test database connectivity from backend

2. Verify demo data exists:
   cd backend
   python scripts/reset_and_seed.py seed

3. Check backend API:
   curl http://localhost:8001/api/v1/health
   curl http://localhost:8001/api/v1/reports/portfolios

4. Review browser console:
   F12 → Console tab → Check for error messages
```

#### 3. AI Chat Not Responding

**Symptoms**:
- Chat messages don't get responses
- "Thinking..." indicator never completes
- Error messages in chat interface

**Solutions**:
```bash
1. Check GPT Agent service:
   curl http://localhost:8888/health

2. Verify OpenAI API key:
   - Check .env file in gptagent directory
   - Ensure OPENAI_API_KEY is set correctly

3. Test backend integration:
   - Ensure backend is accessible from GPT agent
   - Check network connectivity between services

4. Review service logs:
   - Check GPT agent logs for error messages
   - Look for API rate limiting or quota issues
```

#### 4. Performance Issues

**Symptoms**:
- Slow page loading
- Charts take long time to render
- Application feels unresponsive

**Solutions**:
```bash
1. Check system resources:
   - Available memory and CPU usage
   - Database performance and connections
   - Network connectivity speed

2. Optimize browser:
   - Close unnecessary tabs
   - Disable browser extensions temporarily
   - Clear browser cache

3. Database optimization:
   - Check for slow queries
   - Verify database indexes exist
   - Monitor connection pool usage

4. Service optimization:
   - Restart all services
   - Check for memory leaks
   - Review error logs
```

#### 5. Calculation Errors

**Symptoms**:
- Risk metrics showing as N/A or null
- Portfolio values not updating
- Options Greeks missing or incorrect

**Solutions**:
```bash
1. Verify market data:
   - Check if market data providers are accessible
   - Verify API keys are valid and not rate limited
   - Test individual security price lookups

2. Check calculation engines:
   cd backend
   python scripts/test_calculations.py

3. Review position data:
   - Verify all positions have required fields
   - Check for invalid symbols or corrupted data
   - Validate options contract specifications

4. Database integrity:
   - Run data validation scripts
   - Check for missing foreign key relationships
   - Verify calculation result storage
```

### Error Messages

#### Common Error Messages and Solutions

**"Portfolio not found"**
- Ensure you're using correct portfolio ID
- Check that demo data was seeded properly
- Verify database connectivity

**"Calculation failed: insufficient data"**
- Check market data availability for positions
- Verify all required position fields are populated
- Review calculation engine logs for specific gaps

**"Authentication failed"**
- Check JWT token validity
- Verify service-to-service authentication
- Review authentication configuration

**"API rate limit exceeded"**
- Wait for rate limit reset
- Check API key quotas and limits
- Implement request queuing if needed

**"Database connection failed"**
- Verify PostgreSQL is running
- Check database connection strings
- Review network connectivity

### Getting Help

#### Support Resources

**Documentation**:
- This User Guide for operational questions
- API documentation at http://localhost:8001/docs
- Technical documentation in project README files

**Diagnostics**:
- Service health checks via /health endpoints
- Browser developer tools for frontend issues
- Application logs for detailed error information

**Community Resources**:
- GitHub issues for bug reports
- Developer forums for technical questions
- User community for best practices sharing

#### Reporting Issues

**Information to Include**:
1. **Detailed description** of the issue
2. **Steps to reproduce** the problem
3. **Expected behavior** vs actual behavior
4. **Browser and version** information
5. **Error messages** from console or logs
6. **Screenshots** if applicable

**Log Collection**:
```bash
# Backend logs
tail -f backend/logs/sigmasight.log

# Frontend logs
# Check browser developer tools → Console

# GPT Agent logs  
# Check Node.js process output

# Database logs
# Check PostgreSQL log files
```

#### Emergency Procedures

**System Recovery**:
1. **Stop all services** gracefully
2. **Backup current data** if possible
3. **Restart services** in order: Database → Backend → GPT Agent → Frontend
4. **Verify functionality** with health checks
5. **Test critical features** before resuming normal operations

**Data Recovery**:
1. **Check database backups** for recent snapshots
2. **Review transaction logs** for data integrity
3. **Re-run data seeding** if necessary
4. **Validate portfolio calculations** after recovery
5. **Notify users** of any data inconsistencies

---

**Support Contact**: For additional assistance beyond this guide, please refer to your system administrator or the development team.

**Documentation Version**: 1.0  
**Last Updated**: August 26, 2025  
**Next Review**: Quarterly or after major system updates