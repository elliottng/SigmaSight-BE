#!/usr/bin/env python
"""Test script to verify Raw Data API fixes"""

import asyncio
import httpx
from uuid import UUID
import json

async def test_data_endpoints_properly():
    async with httpx.AsyncClient(base_url='http://localhost:8000') as client:
        # Login first
        login_data = {'email': 'demo_individual@sigmasight.com', 'password': 'demo12345'}
        login_response = await client.post('/api/v1/auth/login', json=login_data)
        
        if login_response.status_code != 200:
            print(f'❌ Login failed: {login_response.status_code}')
            return
            
        token = login_response.json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Get user's portfolio ID
        import sys
        from pathlib import Path
        sys.path.append(str(Path(__file__).parent))
        
        from app.database import get_async_session
        from sqlalchemy import select
        from app.models.users import Portfolio, User
        
        async with get_async_session() as db:
            # Get user first
            user_response = await client.get('/api/v1/auth/me', headers=headers)
            user_id = user_response.json()['id']
            
            stmt = select(Portfolio).where(Portfolio.user_id == UUID(user_id))
            result = await db.execute(stmt)
            portfolio = result.scalar_one_or_none()
            if not portfolio:
                print(f'❌ No portfolio found for user')
                return
            portfolio_id = str(portfolio.id)
        
        print(f'✅ Testing with Portfolio ID: {portfolio_id}')
        print('=' * 60)
        
        # Test 1: /data/positions/details with portfolio_id as query parameter
        print('\n1. Testing /data/positions/details with query param...')
        positions_response = await client.get(
            '/api/v1/data/positions/details',
            params={'portfolio_id': portfolio_id},
            headers=headers
        )
        print(f'   Status: {positions_response.status_code}')
        if positions_response.status_code == 200:
            data = positions_response.json()
            print(f'   ✅ Success! Found {len(data.get("positions", []))} positions')
            if "summary" in data:
                print(f'   Total positions: {data["summary"]["total_positions"]}')
        else:
            print(f'   ❌ Error: {positions_response.text[:200]}')
        
        # Test 2: /data/prices/historical with valid portfolio_id
        print('\n2. Testing /data/prices/historical/{portfolio_id}...')
        historical_response = await client.get(
            f'/api/v1/data/prices/historical/{portfolio_id}',
            params={'lookback_days': 30},
            headers=headers
        )
        print(f'   Status: {historical_response.status_code}')
        if historical_response.status_code == 200:
            data = historical_response.json()
            print(f'   ✅ Success! Got historical data')
            if "symbols" in data:
                print(f'   Symbols included: {", ".join(list(data["symbols"].keys())[:5])}...')
        else:
            print(f'   ❌ Error: {historical_response.text[:200]}')
        
        # Test 3: /data/prices/quotes with symbols parameter
        print('\n3. Testing /data/prices/quotes with symbols...')
        quotes_response = await client.get(
            '/api/v1/data/prices/quotes',
            params={'symbols': 'AAPL,MSFT,GOOGL'},
            headers=headers
        )
        print(f'   Status: {quotes_response.status_code}')
        if quotes_response.status_code == 200:
            data = quotes_response.json()
            print(f'   ✅ Success! Got quotes')
            print(f'   Response structure: {list(data.keys())}')
            if "quotes" in data:
                print(f'   Number of quotes: {len(data["quotes"])}')
            elif "data" in data:
                print(f'   Number of quotes (in data): {len(data["data"])}')
        else:
            print(f'   ❌ Error: {quotes_response.text[:200]}')
        
        # Test 4: /data/portfolio/{id}/complete - verify it still works
        print('\n4. Testing /data/portfolio/{id}/complete...')
        complete_response = await client.get(
            f'/api/v1/data/portfolio/{portfolio_id}/complete',
            headers=headers
        )
        print(f'   Status: {complete_response.status_code}')
        if complete_response.status_code == 200:
            data = complete_response.json()
            print(f'   ✅ Still working!')
            print(f'   Portfolio: {data["portfolio"]["name"]}')
        else:
            print(f'   ❌ Error: {complete_response.text[:200]}')
        
        # Test 5: /data/portfolio/{id}/data-quality - check response structure
        print('\n5. Testing /data/portfolio/{id}/data-quality...')
        quality_response = await client.get(
            f'/api/v1/data/portfolio/{portfolio_id}/data-quality',
            headers=headers
        )
        print(f'   Status: {quality_response.status_code}')
        if quality_response.status_code == 200:
            data = quality_response.json()
            print(f'   ✅ Success!')
            print(f'   Response keys: {list(data.keys())}')
            if "position_data_quality" in data:
                pdq = data["position_data_quality"]
                print(f'   Position data quality keys: {list(pdq.keys()) if isinstance(pdq, dict) else "not a dict"}')
        else:
            print(f'   ❌ Error: {quality_response.text[:200]}')
        
        # Test 6: /data/factors/etf-prices - check current state
        print('\n6. Testing /data/factors/etf-prices...')
        etf_response = await client.get(
            '/api/v1/data/factors/etf-prices',
            headers=headers
        )
        print(f'   Status: {etf_response.status_code}')
        if etf_response.status_code == 200:
            data = etf_response.json()
            print(f'   ✅ Endpoint exists')
            print(f'   Response: {data}')
        else:
            print(f'   ❌ Error: {etf_response.text[:200]}')
        
        print('\n' + '=' * 60)
        print('✨ Testing complete!')

if __name__ == "__main__":
    asyncio.run(test_data_endpoints_properly())