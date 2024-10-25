import os
import asyncio
import aiohttp
import toml
from git import Repo
from loguru import logger
from aiohttp import BasicAuth

logger.add(
    'sync.log',
    rotation='1 MB',
    level='DEBUG',
    format='{time} {level} {message}',
)

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.join(PROJECT_DIR, '..', 'repos')
MAX_CONCURRENT_DOWNLOADS = 4


def load_credentials() -> tuple:
    """Load GitHub credentials from the .git-credentials file."""
    with open(os.path.expanduser('~/.git-credentials')) as f:
        credentials = f.read().strip()
    username = credentials.split('/')[2].split(':')[0]
    token = credentials.split('@')[0].split(':')[1]
    return username, token


def load_org_names() -> list:
    """Load organization names from the orgs.toml file."""
    with open(os.path.join(PROJECT_DIR, '../orgs.toml'), 'r') as toml_file:
        data = toml.load(toml_file)
        return data.get('orgs', [])


async def get_repositories(
    session: aiohttp.ClientSession, org_name: str
) -> list:
    """Fetch repositories for a given organization from GitHub API."""
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


def submodule_exists(repo_name: str, org_dir: str) -> bool:
    """Check if a submodule already exists in the .gitmodules file."""
    if os.path.exists(os.path.join(org_dir, '.gitmodules')):
        with open(os.path.join(org_dir, '.gitmodules'), 'r') as f:
            return f'submodule "{repo_name}"' in f.read()
    return False


def add_submodule(repo_url: str, org_name: str) -> None:
    """Add a submodule to the repository."""
    repo_name = os.path.basename(repo_url).replace('.git', '')
    org_dir = os.path.join(REPO_DIR, org_name)

    os.makedirs(org_dir, exist_ok=True)
    os.chdir(org_dir)

    if submodule_exists(repo_name, org_dir):
        logger.warning(
            f"⚠️ Submodule '{repo_name}' already exists. Skipping..."
        )
        return

    try:
        repo = Repo.init()
        repo.create_submodule(repo_name, repo_name, repo_url)
        logger.info(f'✅ Added submodule: {repo_url}')

        if os.path.isdir(repo_name):
            logger.info(f"✅ Submodule '{repo_name}' successfully cloned.")
        else:
            logger.error(f"❌ Error: Submodule '{repo_name}' was not cloned.")
    except Exception as e:
        logger.error(f'❌ Error adding submodule: {repo_url} - {str(e)}')


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


async def main() -> None:
    """Main entry point for the script."""
    global username, token
    username, token = load_credentials()
    org_names = load_org_names()

    async with aiohttp.ClientSession() as session:
        await asyncio.gather(
            *(
                process_organization(session, org_name)
                for org_name in org_names
            )
        )


if __name__ == '__main__':
    asyncio.run(main())
