import os
import subprocess
import shutil
from colorama import init, Fore, Style
from loguru import logger
from config import BRANCH_NAME, SUBMODULES_DIR, GITMODULES_FILE


# Initialize colorama
init(autoreset=True)


def show_help():
    print(f'{Fore.BLUE}💻 Usage: python main.py [options]{Style.RESET_ALL}\n')
    print(f'{Fore.YELLOW}Options:{Style.RESET_ALL}')
    print(f'{Fore.BLUE}--- Submodules ---{Style.RESET_ALL}')
    print('  -s, --sync             🔄 Sync submodules')
    print('  -c, --commit           📝 Commit changes in submodules')
    print('  -p, --push             🚀 Push changes in submodules')
    print('  -r, --remove ORG/REPO  ❌ Remove a specific submodule\n')
    print(f'{Fore.BLUE}--- Main Project ---{Style.RESET_ALL}')
    print(
        '  -m, --main-commit      💾 Commit changes in the main project only'
    )
    print(
        '  -p-main, --push-main    🚀 Push changes in the main project only\n'
    )
    print(f'{Fore.BLUE}--- Danger Zone ---{Style.RESET_ALL}')
    print(
        '  -cm, --commit-all      🔥 Commit changes in both main project and submodules'
    )
    print(
        '  -a, --all-push         🔥 Push all changes (submodules and main project)\n'
    )
    print(
        f'{Fore.YELLOW}⚠️ Warning: Commands that modify submodules can potentially overwrite changes.{Style.RESET_ALL}'
    )


def check_error(result):
    if result.returncode != 0:
        logger.error('Failed to execute the previous command.')
        exit(1)


def run_git_command(command):
    result = subprocess.run(command, capture_output=True, text=True)
    check_error(result)
    return result


def sync_submodules():
    logger.info('🔄 Updating submodules...')
    run_git_command(['git', 'submodule', 'update', '--remote'])


def commit_submodule_changes():
    logger.info('🔍 Checking for changes in submodules...')
    result = run_git_command(
        [
            'git',
            'submodule',
            'foreach',
            '--recursive',
            'git status --porcelain',
        ]
    )

    if result.stdout.strip():
        commit_message = input('✏️ Enter commit message for submodules: ')
        run_git_command(
            [
                'git',
                'submodule',
                'foreach',
                '--recursive',
                f"git add . && git commit -m '{commit_message}'",
            ]
        )
        logger.success('✅ Submodules committed successfully.')
    else:
        logger.info('✅ No changes found in submodules.')


def push_submodule_changes():
    logger.info('🚀 Pushing changes in submodules...')
    run_git_command(['git', 'submodule', 'foreach', '--recursive', 'git push'])


def commit_main_project():
    logger.info('💾 Committing changes in the main project...')
    message = input('✏️ Enter commit message for the main project: ')
    run_git_command(['git', 'add', '.'])
    run_git_command(['git', 'commit', '-m', message])
    logger.success('✅ Main project committed successfully.')


def push_main_project():
    logger.info('🚀 Pushing changes in the main project...')
    result = run_git_command(['git', 'remote', '-v'])

    if not result.stdout.strip():
        remote_url = input(
            '🔗 Enter the remote repository URL (e.g., https://github.com/username/repo.git): '
        )
        run_git_command(['git', 'remote', 'add', 'origin', remote_url])
        logger.success(f'✅ Remote repository added as origin: {remote_url}')

    try:
        run_git_command(
            ['git', 'push', '--set-upstream', 'origin', BRANCH_NAME]
        )
    except SystemExit:
        logger.warning('Push failed. Attempting to pull changes...')
        handle_push_failure()


def handle_push_failure():
    pull_choice = input(
        'Do you want to pull the latest changes from the remote? (y/n): '
    )
    if pull_choice.lower() == 'y':
        logger.info('Fetching and merging changes from the remote...')
        run_git_command(['git', 'fetch', 'origin'])
        run_git_command(['git', 'merge', f'origin/{BRANCH_NAME}'])
        logger.info('Retrying push...')
        run_git_command(['git', 'push', 'origin', BRANCH_NAME])
    else:
        logger.warning(
            'You chose not to pull changes. Please resolve the conflict manually.'
        )


def remove_submodule(org_repo):
    repo_path = os.path.join(SUBMODULES_DIR, org_repo)
    if not os.path.isdir(repo_path):
        logger.error(
            f"Repository '{repo_path}' does not exist as a submodule."
        )
        exit(1)

    logger.info(f"🗑 Removing submodule '{org_repo}'...")
    run_git_command(
        [
            'git',
            'config',
            '--file',
            GITMODULES_FILE,
            '--remove-section',
            f'submodule.{repo_path}',
        ]
    )
    run_git_command(
        ['git', 'config', '--remove-section', f'submodule.{repo_path}']
    )
    shutil.rmtree(repo_path)
    run_git_command(['git', 'rm', '--cached', repo_path])
    run_git_command(['git', 'add', GITMODULES_FILE])
    run_git_command(['git', 'commit', '-m', f'Remove submodule {org_repo}'])
    logger.success(f"✅ Submodule '{org_repo}' removed successfully.")


def commit_all_changes():
    logger.info(
        '💾 Committing changes in both the main project and all submodules...'
    )
    commit_main_project()

    result = run_git_command(
        [
            'git',
            'submodule',
            'foreach',
            '--recursive',
            'git status --porcelain',
        ]
    )
    if result.stdout.strip():
        commit_message = input('✏️ Enter commit message for submodules: ')
        run_git_command(
            [
                'git',
                'submodule',
                'foreach',
                '--recursive',
                f"git add . && git commit -m '{commit_message}'",
            ]
        )
        logger.success('✅ All submodules committed successfully.')
    else:
        logger.info('✅ No changes found in submodules.')


def push_all_changes():
    logger.info('🔥 Pushing all changes (submodules and main project)...')
    push_submodule_changes()
    push_main_project()


if __name__ == '__main__':
    show_help()

