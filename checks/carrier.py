import json
import aiopg
import asyncio
from datetime import datetime, timedelta

from aiologger import Logger

logger = Logger.with_default_handlers()

class CarrierCheck:

    def __init__(self, host, port, dbname, user, password) -> None:
        super().__init__()
        self.dsn = "host={} port={} dbname={} user={} password={}".format(
            host, port, dbname, user, password
        )

    async def fetch_result(self, cursor):
        await cursor.execute("SELECT result FROM carrier_status;")
        return await cursor.fetchall()

    async def carrier_healthcheck(self):
        checks = []
        pool = await aiopg.create_pool(self.dsn)
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                query_result = await self.fetch_result(cur)
                if len(query_result) < 2:
                    asyncio.sleep(1)
                    query_result = await self.fetch_result(cur)

                if len(query_result) == 2:
                    for row in query_result:
                        data = json.loads(row[0])
                        logger.info(f"[CarrierCheck] CarrierStatus data:{data}")
                        if data.get("created_at", None):
                            parsed = datetime.fromisoformat(data.get("created_at"))
                            if (datetime.utcnow() - timedelta(minutes=2)) <= parsed:
                                checks.append(True if data.get("status", None) == 200 else False)
                            else:
                                checks.append(False)
                        else:
                            checks.append(False)
                else:
                    logger.info(f"[CarrierCheck] QueryResult:{query_result}")
                    checks.append(False)

        return {
        'status': 200 if all(checks) else 500,
        "carrier": all(checks),
        "created_at": str(datetime.utcnow())
        }


    async def check(self):
        return await self.carrier_healthcheck()