import os
from git import Repo
from logger import logger
from constants import REPO_DIR


def submodule_exists(repo_name: str, org_dir: str) -> bool:
    if os.path.exists(os.path.join(org_dir, '.gitmodules')):
        with open(os.path.join(org_dir, '.gitmodules'), 'r') as f:
            return f'submodule "{repo_name}"' in f.read()
    return False


def add_submodule(repo_url: str, org_name: str) -> None:
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
