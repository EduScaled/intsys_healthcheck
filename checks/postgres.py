import aiopg

class PostgresResponseCheck:

    def __init__(self, host, port, dbname, user, password) -> None:
        super().__init__()
        self.dsn = "host={} port={} dbname={} user={} password={}".format(
            host, port, dbname, user, password
        )

    async def postgres_healthcheck(self):
        pool = await aiopg.create_pool(self.dsn)
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT 1")
                ret = []
                async for row in cur:
                    ret.append(row)
                return True if ret == [(1,)] else False

    async def check(self):
        return await self.postgres_healthcheck()