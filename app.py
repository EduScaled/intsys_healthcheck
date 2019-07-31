import json

import aiopg
import asyncio
from typing import Callable

import datetime
import sentry_sdk
from aiohttp import web
from sentry_sdk import capture_exception
from sentry_sdk.integrations.aiohttp import AioHttpIntegration

from checks.carrier import CarrierCheck
from checks.culture import CultureCheck
from checks.postgres import PostgresResponseCheck
from checks.uploads import UploadsCheck
from settings import settings

from aiologger import Logger

logger = Logger.with_default_handlers()


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
    logger.info(f"[DBCheck] {result}")
    return web.json_response(result, status=status)


async def culture_healthcheck(_):
    result = await CultureCheck(
        settings.DB_HOST, settings.DB_PORT, settings.DB_NAME, settings.DB_USER,  settings.DB_PASSWORD
    ).check()
    status = 200 if str(result.get("status", None)) == "200" else 500
    logger.info(f"[CultureCheck] {result}")
    return web.json_response(result, status=status)


async def uploads_healthcheck(_):
    result = await UploadsCheck(
        settings.DB_HOST, settings.DB_PORT, settings.DB_NAME, settings.DB_USER,  settings.DB_PASSWORD
    ).check()
    status = 200 if str(result.get("status", None)) == "200" else 500
    logger.info(f"[UploadsCheck] {result}")
    return web.json_response(result, status=status)


async def carrier_healthcheck(_):
    result = await CarrierCheck(
        settings.DB_HOST, settings.DB_PORT, settings.DB_NAME, settings.DB_USER,  settings.DB_PASSWORD
    ).check()
    status = 200 if str(result.get("status", None)) == "200" else 500
    logger.info(f"[CarrierCheck] {result}")
    return web.json_response(result, status=status)


async def carrier_callback(request):
    json_request = await request.json()
    if json_request['topic'] == 'healthcheck':
        logger.info(f"[CarrierCheck] got healthcheck callback.")
        pool = await aiopg.create_pool("host={} port={} dbname={} user={} password={}".format(
            settings.DB_HOST, settings.DB_PORT, settings.DB_NAME, settings.DB_USER, settings.DB_PASSWORD
        ))
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT message FROM carrier_message")
                query_result = await cur.fetchall()
                if query_result[0][0] == json_request['value'].replace('"',''):
                    kafka_read_result = {
                        "carrier-kafka-read": True,
                        "status": 200,
                        "created_at": str(datetime.datetime.utcnow())
                    }
                    await cur.execute(
                        "INSERT INTO carrier_status (result) VALUES ('{}')".format(
                            json.dumps(kafka_read_result)
                        ))
                    conn.commit()
                    logger.info(f"[CarrierCheck] callback read and saved to db.")
                else:
                    logger.info(f'''
                    [CarrierCheck] callback not processed.
                    Stored  {query_result[0][0]} and Received {json_request['value'].replace('"','')}
                    messages is not equal.''')

    return web.Response(status=200)


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
        logger.info(f"[Settings] updated.")
        return web.Response(status=200)

    logger.info(f"[Settings] not updated.")
    return web.Response(status=400)


def init_func():
    logger.info(f"[HealthCheck] started.")
    app = web.Application()
    app.add_routes([
        web.get('/healthcheck/culture', culture_healthcheck),
        web.get('/healthcheck/uploads', uploads_healthcheck),
        web.get('/healthcheck/db', db_healthcheck),
        web.get('/healthcheck/carrier', carrier_healthcheck),
        web.post('/carrier/callback', carrier_callback),
        web.post('/healthcheck/settings/update', update_settings),
    ])
    return app
