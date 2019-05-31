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
                await cur.execute("SELECT COUNT(*) FROM pg_catalog.pg_tables;")
                ret = []
                for row in await cur.fetchall():
                    ret.append(row)
                # ret should be equal to [(x,)], where x is int > 0
                return True if len(ret) == 1 and len(ret[0]) == 1 and ret[0][0] != 0 else False

    async def check(self):
        return await self.postgres_healthcheck()