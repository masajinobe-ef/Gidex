import asyncio
import aiohttp
import sys
from logger import logger
from repo import process_organization
from credentials import load_credentials
from org_loader import load_org_names
from operations import (
    show_help,
    sync_submodules,
    commit_submodule_changes,
    push_submodule_changes,
    commit_main_project,
    push_main_project,
    remove_submodule,
    # remove_org_folder,
)


async def initialize() -> None:
    logger.info('Initializing the repositories...')

    try:
        load_credentials()
    except Exception as e:
        logger.error(f'❌ Error loading credentials: {e}')
        return

    try:
        org_names = load_org_names()
    except Exception as e:
        logger.error(f'❌ Error loading organization names: {e}')
        return

    try:
        async with aiohttp.ClientSession() as session:
            await asyncio.gather(
                *(
                    process_organization(session, org_name)
                    for org_name in org_names
                )
            )
    except Exception as e:
        logger.error(f'❌ Error processing organizations: {e}')
        return

    logger.info('Initialization complete.')


async def main() -> None:
    if len(sys.argv) < 2:
        logger.error('❌ Error: No arguments provided.')
        show_help()
        exit(1)

    option = sys.argv[1]

    try:
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

        # elif option in ['-ro', '--remove-org']:
        #     if len(sys.argv) < 3:
        #         logger.error('❌ Error: No organization specified to remove.')
        #         show_help()
        #         exit(1)
        #
        #     remove_org_folder(sys.argv[2])

        elif option in ['-h', '--help']:
            show_help()

        elif option in ['-i', '--init']:
            await initialize()

        else:
            logger.error('❌ Error: Unknown argument.')
            show_help()
    except Exception as e:
        logger.error(f'❌ An error occurred while processing the command: {e}')


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f'❌ An unexpected error occurred: {e}')

