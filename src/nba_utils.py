from timeit import default_timer
import asyncio
import aiohttp


async def fetch(session, url: str):
    async with session.get(url, ssl=False) as response:
        data = await response.read()
        return data


async def fetch_api_data(urls: list) -> tuple:
    print("Fetching api data...")
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in urls:
            tasks.append(fetch(session, url))
        responses = await asyncio.gather(*tasks, return_exceptions=False)
    return responses


def time_func(func):
    def wrapper(*args, **kwargs):
        start = default_timer()
        result = func(*args, **kwargs)
        end = default_timer()
        print(end - start)
        return result

    return wrapper
