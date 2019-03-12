import json
import aiopg
import asyncio
from datetime import datetime, timedelta


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
                    from pprint import pprint
                    pprint(query_result[0])
                    
                    data = json.loads(query_result[0][0])
                    pprint(data)

                    if data.get("created_at", None):
                        parsed = datetime.fromisoformat(data.get("created_at"))
                        if (datetime.utcnow() - timedelta(minutes=2)) <= parsed:
                            result = data
                        else:
                            data["status"] = 500
                            result = data
                    else:
                        result = { "status": 500, "db": "false" }
                else:
                    result = { "status": 500, "db": "false" }
                        
                return result

    async def check(self):
        return await self.culture_healthcheck()