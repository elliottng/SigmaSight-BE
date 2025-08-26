#!/usr/bin/env python
"""Test script for the new /data/ namespace endpoints - handles actual response structures"""

import asyncio
import httpx
from datetime import datetime
import json

async def test_data_endpoints():
    async with httpx.AsyncClient(base_url='http://localhost:8000') as client:
        # Login first - using demo credentials
        login_data = {'email': 'demo_individual@sigmasight.com', 'password': 'demo12345'}
        login_response = await client.post('/api/v1/auth/login', json=login_data)
        
        if login_response.status_code != 200:
            print(f'❌ Login failed: {login_response.status_code}')
            print(login_response.text)
            return
            
        token = login_response.json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        print(f'✅ Logged in successfully')
        
        # Get user info to derive portfolio ID (since portfolio endpoint is not implemented)
        user_response = await client.get('/api/v1/auth/me', headers=headers)
        if user_response.status_code != 200:
            print(f'❌ User info fetch failed: {user_response.status_code}')
            return
            
        user_id = user_response.json()['id']
        
        # Get portfolio ID directly from database (temporary until portfolio endpoint is implemented)
        import sys
        from pathlib import Path
        sys.path.append(str(Path(__file__).parent))
        
        from app.database import get_async_session
        from sqlalchemy import select
        from app.models.users import Portfolio
        from uuid import UUID
        
        async with get_async_session() as db:
            stmt = select(Portfolio).where(Portfolio.user_id == UUID(user_id))
            result = await db.execute(stmt)
            portfolio = result.scalar_one_or_none()
            if not portfolio:
                print(f'❌ No portfolio found for user')
                return
            portfolio_id = str(portfolio.id)
        
        print(f'✅ Got portfolio ID: {portfolio_id}')
        print('=' * 60)
        
        # Test /data/portfolio/{id}/complete
        print('\n📊 Testing /data/portfolio/{id}/complete...')
        complete_response = await client.get(f'/api/v1/data/portfolio/{portfolio_id}/complete', headers=headers)
        print(f'   Status: {complete_response.status_code}')
        if complete_response.status_code == 200:
            data = complete_response.json()
            if "portfolio" in data:
                print(f'   ✅ Portfolio: {data["portfolio"]["name"]}')
                print(f'      Total Value: ${data["portfolio"]["total_value"]:,.2f}')
                print(f'      Positions: {data["portfolio"]["position_count"]}')
            if "positions_summary" in data:
                print(f'      Long Positions: {data["positions_summary"]["long_count"]}')
                print(f'      Short Positions: {data["positions_summary"]["short_count"]}')
        else:
            print(f'   ❌ Error: {complete_response.text[:200]}')
        
        print('=' * 60)
        
        # Test /data/portfolio/{id}/data-quality
        print('\n🔍 Testing /data/portfolio/{id}/data-quality...')
        quality_response = await client.get(f'/api/v1/data/portfolio/{portfolio_id}/data-quality', headers=headers)
        print(f'   Status: {quality_response.status_code}')
        if quality_response.status_code == 200:
            data = quality_response.json()
            print(f'   ✅ Data Quality Assessment:')
            if "position_data_quality" in data:
                pdq = data["position_data_quality"]
                print(f'      Total Positions: {pdq.get("total_positions", "N/A")}')
                print(f'      With Market Data: {pdq.get("positions_with_market_data", "N/A")}')
                print(f'      Missing Data: {pdq.get("positions_missing_data", "N/A")}')
            if "calculation_feasibility" in data:
                cf = data["calculation_feasibility"]
                print(f'      Can Calculate Greeks: {cf.get("can_calculate_greeks", "N/A")}')
                print(f'      Can Calculate Factors: {cf.get("can_calculate_factors", "N/A")}')
        else:
            print(f'   ❌ Error: {quality_response.text[:200]}')
            
        print('=' * 60)
        
        # Test /data/positions/{id}/details
        print(f'\n📈 Testing /data/positions/{portfolio_id}/details...')
        positions_response = await client.get(f'/api/v1/data/positions/{portfolio_id}/details', headers=headers)
        print(f'   Status: {positions_response.status_code}')
        if positions_response.status_code == 200:
            data = positions_response.json()
            if "summary" in data:
                print(f'   ✅ Positions Summary:')
                print(f'      Total: {data["summary"]["total_count"]}')
                print(f'      Long: {data["summary"]["long_count"]}')
                print(f'      Short: {data["summary"]["short_count"]}')
            if "positions" in data and len(data["positions"]) > 0:
                print(f'   Sample positions (first 3):')
                for pos in data["positions"][:3]:
                    print(f'      - {pos["symbol"]}: {pos["quantity"]} shares @ ${pos.get("last_price", 0):.2f}')
        elif positions_response.status_code == 404:
            print(f'   ⚠️ Endpoint not found - may not be implemented yet')
        else:
            print(f'   ❌ Error: {positions_response.text[:200]}')
            
        print('=' * 60)
        
        # Test /data/prices/historical
        print('\n📉 Testing /data/prices/historical...')
        historical_params = {'symbol': 'AAPL', 'days': 30}
        historical_response = await client.get('/api/v1/data/prices/historical', headers=headers, params=historical_params)
        print(f'   Status: {historical_response.status_code}')
        if historical_response.status_code == 200:
            data = historical_response.json()
            print(f'   ✅ Historical Prices:')
            print(f'      Symbol: {data.get("symbol", "N/A")}')
            if "metadata" in data:
                print(f'      Data Points: {data["metadata"].get("data_points", "N/A")}')
            if "prices" in data and len(data["prices"]) > 0:
                print(f'      Latest Price: ${data["prices"][0].get("close", 0):.2f} on {data["prices"][0].get("date", "N/A")}')
        elif historical_response.status_code == 404:
            print(f'   ⚠️ Endpoint not found - may not be implemented yet')
        else:
            print(f'   ❌ Error: {historical_response.text[:200]}')
            
        print('=' * 60)
        
        # Test /data/prices/quotes
        print('\n💹 Testing /data/prices/quotes...')
        quotes_params = {'symbols': 'AAPL,MSFT,GOOGL'}
        quotes_response = await client.get('/api/v1/data/prices/quotes', headers=headers, params=quotes_params)
        print(f'   Status: {quotes_response.status_code}')
        if quotes_response.status_code == 200:
            data = quotes_response.json()
            if isinstance(data, list):
                print(f'   ✅ Quotes Retrieved: {len(data)} quotes')
                for quote in data[:3]:
                    if isinstance(quote, dict):
                        print(f'      - {quote.get("symbol", "N/A")}: ${quote.get("price", 0):.2f}')
            elif isinstance(data, dict):
                if "quotes" in data:
                    print(f'   ✅ Quotes Retrieved: {len(data["quotes"])} quotes')
                    for quote in data["quotes"][:3]:
                        print(f'      - {quote.get("symbol", "N/A")}: ${quote.get("price", 0):.2f}')
                else:
                    print(f'   Response structure: {list(data.keys())}')
        else:
            print(f'   ❌ Error: {quotes_response.text[:200]}')
            
        print('=' * 60)
        print('\n✨ Test completed!')

if __name__ == "__main__":
    asyncio.run(test_data_endpoints())