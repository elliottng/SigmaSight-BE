#!/usr/bin/env python
"""Test script for the new /data/ namespace endpoints"""

import asyncio
import httpx
from datetime import datetime

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
        
        # Test /data/portfolio/{id}/complete
        print('\nTesting /data/portfolio/{id}/complete...')
        complete_response = await client.get(f'/api/v1/data/portfolio/{portfolio_id}/complete', headers=headers)
        print(f'Status: {complete_response.status_code}')
        if complete_response.status_code == 200:
            data = complete_response.json()
            print(f'✅ Portfolio: {data["portfolio"]["name"]}')
            print(f'   Total Value: ${data["portfolio"]["total_value"]:,.2f}')
            print(f'   Positions: {data["portfolio"]["position_count"]}')
        else:
            print(f'❌ Error: {complete_response.text[:500]}')
        
        # Test /data/portfolio/{id}/data-quality
        print('\nTesting /data/portfolio/{id}/data-quality...')
        quality_response = await client.get(f'/api/v1/data/portfolio/{portfolio_id}/data-quality', headers=headers)
        print(f'Status: {quality_response.status_code}')
        if quality_response.status_code == 200:
            data = quality_response.json()
            print(f'✅ Data Quality Check:')
            # Check if summary exists first
            if "summary" in data:
                print(f'   Positions: {data["summary"]["total_positions"]}')
                print(f'   Complete: {data["summary"]["complete_data"]}')
            else:
                print(f'   Response keys: {list(data.keys())}')
        else:
            print(f'❌ Error: {quality_response.text[:500]}')
            
        # Test /data/positions/{id}/details
        print('\nTesting /data/positions/{id}/details...')
        positions_response = await client.get(f'/api/v1/data/positions/{portfolio_id}/details', headers=headers)
        print(f'Status: {positions_response.status_code}')
        if positions_response.status_code == 200:
            data = positions_response.json()
            print(f'✅ Positions Count: {data["summary"]["total_count"]}')
            print(f'   Long: {data["summary"]["long_count"]}')
            print(f'   Short: {data["summary"]["short_count"]}')
        else:
            print(f'❌ Error: {positions_response.text[:500]}')
            
        # Test /data/prices/historical
        print('\nTesting /data/prices/historical...')
        historical_params = {'symbol': 'AAPL', 'days': 30}
        historical_response = await client.get('/api/v1/data/prices/historical', headers=headers, params=historical_params)
        print(f'Status: {historical_response.status_code}')
        if historical_response.status_code == 200:
            data = historical_response.json()
            print(f'✅ Symbol: {data["symbol"]}')
            print(f'   Data Points: {data["metadata"]["data_points"]}')
        else:
            print(f'❌ Error: {historical_response.text[:500]}')
            
        # Test /data/prices/quotes  
        print('\nTesting /data/prices/quotes...')
        quotes_params = {'symbols': 'AAPL,MSFT,GOOGL'}
        quotes_response = await client.get('/api/v1/data/prices/quotes', headers=headers, params=quotes_params)
        print(f'Status: {quotes_response.status_code}')
        if quotes_response.status_code == 200:
            data = quotes_response.json()
            print(f'✅ Quotes Retrieved: {len(data["quotes"])}')
            for quote in data["quotes"][:3]:
                print(f'   {quote["symbol"]}: ${quote["price"]:.2f}')
        else:
            print(f'❌ Error: {quotes_response.text[:500]}')

if __name__ == "__main__":
    asyncio.run(test_data_endpoints())