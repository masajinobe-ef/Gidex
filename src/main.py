import asyncio
import aiohttp
import sys
from credentials import load_credentials
from org_loader import load_org_names
from git_repo import process_organization
from git_operations import (
    show_help,
    sync_submodules,
    commit_submodule_changes,
    push_submodule_changes,
    commit_main_project,
    push_main_project,
    remove_submodule,
)


async def main() -> None:
    """Main entry point for the script."""
    load_credentials()  # To ensure credentials are available before starting
    org_names = load_org_names()

    async with aiohttp.ClientSession() as session:
        await asyncio.gather(
            *(
                process_organization(session, org_name)
                for org_name in org_names
            )
        )

    if len(sys.argv) < 2:
        print('Error: No arguments provided.')
        show_help()
        exit(1)

    option = sys.argv[1]
    if option in ['-s', '--sync']:
        sync_submodules()
    elif option in ['-c', '--commit']:
        commit_submodule_changes()
    elif option in ['-p', '--push']:
        push_submodule_changes()
    elif option in ['-m', '--main-commit']:
        commit_main_project()
    elif option in ['-p-main', '--push-main']:
        push_main_project()
    elif option in ['-r', '--remove']:
        if len(sys.argv) < 3:
            print('Error: No submodule specified to remove.')
            show_help()
            exit(1)
        remove_submodule(sys.argv[2])
    elif option in ['-h', '--help']:
        show_help()
    else:
        print('Error: Unknown argument.')
        show_help()


if __name__ == '__main__':
    asyncio.run(main())
