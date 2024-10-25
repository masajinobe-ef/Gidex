import aiohttp
from aiohttp import BasicAuth
import asyncio
from credentials import load_credentials
from logger import logger
from config import MAX_CONCURRENT_DOWNLOADS
from git_submodule import add_submodule


async def get_repositories(
    session: aiohttp.ClientSession, org_name: str
) -> list:
    """Fetch repositories for a given organization from GitHub API."""
    username, token = load_credentials()
    page = 1
    repos = []

    while True:
        async with session.get(
            f'https://api.github.com/orgs/{org_name}/repos?per_page=100&page={page}',
            auth=BasicAuth(username, token),
        ) as response:
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
    """Process an organization by fetching its repositories and adding them as submodules."""
    logger.info(f'🔍 Processing organization: {org_name}')
    repos = await get_repositories(session, org_name)

    if not repos:
        logger.warning(f'⚠️ No repositories found for organization: {org_name}')
        return

    semaphore = asyncio.Semaphore(MAX_CONCURRENT_DOWNLOADS)

    async def limited_add_submodule(repo):
        """Limit the number of concurrent submodule additions."""
        async with semaphore:
            await asyncio.to_thread(add_submodule, repo, org_name)

    await asyncio.gather(*(limited_add_submodule(repo) for repo in repos))
