import asyncio
import aiohttp
import sys

# Loguru
from utils.logger import logger

# Git
from git.repo import process_organization
from git.credentials import load_credentials
from git.operations import (
    show_help,
    sync_submodules,
    commit_submodule_changes,
    push_submodule_changes,
    commit_main_project,
    push_main_project,
    remove_submodule,
)


from utils.org_loader import load_org_names


async def main() -> None:
    load_credentials()
    org_names = load_org_names()

    async with aiohttp.ClientSession() as session:
        await asyncio.gather(
            *(
                process_organization(session, org_name)
                for org_name in org_names
            )
        )

    if len(sys.argv) < 2:
        logger.error('❌ Error: No arguments provided.')
        show_help()
        exit(1)

    option = sys.argv[1]
    if option in ['-s', '--sync']:
        sync_submodules()
    elif option in ['-c', '--commit']:
        commit_submodule_changes()
    elif option in ['-p', '--push']:
        push_submodule_changes()
    elif option in ['-mc', '--main-commit']:
        commit_main_project()
    elif option in ['-pm', '--push-main']:
        push_main_project()
    elif option in ['-r', '--remove']:
        if len(sys.argv) < 3:
            logger.error('❌ Error: No submodule specified to remove.')
            show_help()
            exit(1)
        remove_submodule(sys.argv[2])
    elif option in ['-h', '--help']:
        show_help()
    else:
        logger.error('❌ Error: Unknown argument.')
        show_help()


if __name__ == '__main__':
    asyncio.run(main())
