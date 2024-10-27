import aiohttp
from aiohttp import BasicAuth
import asyncio
from logger import logger
from config import MAX_CONCURRENT_DOWNLOADS
from submodule import add_submodule
from credentials import load_credentials


async def get_repositories(
    session: aiohttp.ClientSession, org_name: str
) -> list:
    username, token = load_credentials()
    page = 1
    repos = []

    while True:
        async with session.get(
            f'https://api.github.com/orgs/{
                org_name}/repos?per_page=100&page={page}',
            auth=BasicAuth(username, token),
        ) as response:
            if response.status == 403:
                error_message = (await response.json()).get(
                    'message', 'API rate limit exceeded'
                )
                logger.error(
                    f'❌ Error fetching repos for {org_name}: {error_message}'
                )
                logger.warning(
                    f'⚠️ Rate limit exceeded for organization: {
                        org_name}. Please try again later.'
                )
                return []

            if response.status != 200:
                error_message = (await response.json()).get(
                    'message', 'Unknown error'
                )
                logger.error(
                    f'❌ Error fetching repos for {org_name}: {error_message}'
                )
                return []

            clone_urls = [repo['clone_url'] for repo in await response.json()]

            if not clone_urls:
                break

            repos.extend(clone_urls)

            if len(clone_urls) < 100:
                break

            page += 1

    return repos


async def process_organization(
    session: aiohttp.ClientSession, org_name: str
) -> None:
    logger.info(f'🔍 Processing organization: {org_name}')
    repos = await get_repositories(session, org_name)

    if not repos:
        logger.warning(f'⚠️ No repositories found for organization: {org_name}')
        return

    semaphore = asyncio.Semaphore(MAX_CONCURRENT_DOWNLOADS)

    async def limited_add_submodule(repo):
        async with semaphore:
            await asyncio.to_thread(add_submodule, repo, org_name)

    await asyncio.gather(*(limited_add_submodule(repo) for repo in repos))
