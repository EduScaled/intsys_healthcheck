import json
import aiopg
import asyncio
from datetime import datetime, timedelta

from aiologger import Logger

logger = Logger.with_default_handlers()

class CultureCheck:

    def __init__(self, host, port, dbname, user, password) -> None:
        super().__init__()
        self.dsn = "host={} port={} dbname={} user={} password={}".format(
            host, port, dbname, user, password
        )

    async def fetch_result(self, cursor):
        await cursor.execute("SELECT result FROM intsys_status;")
        return await cursor.fetchall()

    async def culture_healthcheck(self):
        pool = await aiopg.create_pool(self.dsn)
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                query_result = await self.fetch_result(cursor)
                if len(query_result) == 0:
                    asyncio.sleep(1)
                    query_result = await self.fetch_result(cursor)

                if len(query_result) == 1:
                    data = json.loads(query_result[0][0])
                    logger.info(f"[CultureCheck] CultureStatus data:{data}")
                    if data.get("created_at", None):
                        parsed = datetime.fromisoformat(data.get("created_at"))
                        if (datetime.utcnow() - timedelta(minutes=2)) <= parsed:
                            result = data
                        else:
                            data["status"] = 500
                            result = data
                    else:
                        result = { "status": 500, "db": "field 'created_at' not found" }
                else:
                    logger.info(f"[CultureCheck] QueryResult:{query_result}")
                    result = { "status": 500, "db": "query result length doesn't equal 1" }
                        
                return result

    async def check(self):
        return await self.culture_healthcheck()