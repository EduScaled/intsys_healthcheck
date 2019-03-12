from typing import List

from settings import settings


class Check:
    async def check(self, **kwargs):
        raise NotImplementedError()