import json

import aiopg
import asyncio
from typing import Callable

import sentry_sdk
from aiohttp import web
from sentry_sdk import capture_exception
from sentry_sdk.integrations.aiohttp import AioHttpIntegration

from checks.culture import CultureCheck
from checks.postgres import PostgresResponseCheck
from settings import settings

sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    environment=settings.SENTRY_ENVIRONMENT,
    integrations=[AioHttpIntegration()]
)


async def run_check(f: Callable, **kwargs):
    try:
        return await f(**kwargs)
    except Exception as e:
        capture_exception(e)
        return False

async def db_healthcheck(_):
    result = await PostgresResponseCheck(
        settings.DB_HOST, settings.DB_PORT, settings.DB_NAME, settings.DB_USER,  settings.DB_PASSWORD
    ).check()
    status = 200 if result else 500
    result = { "status": status, "db": str(status == 200).lower() }
    
    return web.json_response(result, status=status)

async def culture_healthcheck(_):
    result = await CultureCheck(
        settings.DB_HOST, settings.DB_PORT, settings.DB_NAME, settings.DB_USER,  settings.DB_PASSWORD
    ).check()
    status = 200 if str(result.get("status", None)) == "200" else 500

    return web.json_response(result, status=status)


async def update_settings(request):
    update_query = """
        INSERT INTO settings (name, value)
        VALUES ('is_enabled', '{value}')
        ON CONFLICT (name)
        DO UPDATE SET
        value='{value}';
        """
    post_data = await request.json()
    is_enabled = post_data.get('is_enabled', None)
    if is_enabled:
        pool = await aiopg.create_pool("host={} port={} dbname={} user={} password={}".format(
            settings.DB_HOST, settings.DB_PORT, settings.DB_NAME, settings.DB_USER, settings.DB_PASSWORD
            ))
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(update_query.format(value=is_enabled))
                conn.commit()
        return web.Response(status=200)

    return web.Response(status=400)

def init_func():
    app = web.Application()
    app.add_routes([
        web.get('/healthcheck/culture', culture_healthcheck),
        web.get('/healthcheck/db', db_healthcheck),
        web.post('/healthcheck/settings/update', update_settings),
    ])
    return app
