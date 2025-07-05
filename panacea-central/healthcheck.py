#!/usr/bin/env python3
import asyncio
import aiohttp
import json
from datetime import datetime

async def check_panacea_health():
    """Verificar salud de Panacea API Central"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://panacea-api-central:8000/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Panacea API Central: {data}")
                    return True
                else:
                    print(f"❌ Panacea API Central error: {response.status}")
                    return False
    except Exception as e:
        print(f"❌ Error conectando con Panacea: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(check_panacea_health())
    exit(0 if result else 1)
