import os
import subprocess
from colorama import init, Fore, Style


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
        print(
            f'{Fore.RED}Error: Failed to execute the previous command.{Style.RESET_ALL}'
        )
        exit(1)


def sync_submodules():
    print(f'{Fore.GREEN}🔄 Updating submodules...{Style.RESET_ALL}')
    result = subprocess.run(['git', 'submodule', 'update', '--remote'])
    check_error(result)


def commit_submodule_changes():
    print(
        f'{Fore.GREEN}🔍 Checking for changes in submodules...{Style.RESET_ALL}'
    )
    result = subprocess.run(
        [
            'git',
            'submodule',
            'foreach',
            '--recursive',
            'git status --porcelain',
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0 and result.stdout.strip():
        commit_message = input('✏️ Enter commit message for submodules: ')
        subprocess.run(
            [
                'git',
                'submodule',
                'foreach',
                '--recursive',
                f"git add . && git commit -m '{commit_message}'",
            ]
        )
        check_error(result)
    else:
        print(
            f'{Fore.GREEN}✅ No changes found in submodules.{Style.RESET_ALL}'
        )


def push_submodule_changes():
    print(f'{Fore.GREEN}🚀 Pushing changes in submodules...{Style.RESET_ALL}')
    result = subprocess.run(
        ['git', 'submodule', 'foreach', '--recursive', 'git push']
    )
    check_error(result)


def commit_main_project():
    print(
        f'{Fore.GREEN}💾 Committing changes in the main project...{Style.RESET_ALL}'
    )
    message = input('✏️ Enter commit message for the main project: ')
    result = subprocess.run(['git', 'add', '.'])
    check_error(result)
    result = subprocess.run(['git', 'commit', '-m', message])
    check_error(result)


def push_main_project():
    print(
        f'{Fore.GREEN}🚀 Pushing changes in the main project...{Style.RESET_ALL}'
    )

    # Check for existing remotes
    result = subprocess.run(
        ['git', 'remote', '-v'], capture_output=True, text=True
    )

    # If there are no remotes, prompt for a URL
    if result.returncode != 0 or not result.stdout.strip():
        print(f'{Fore.RED}No remote repository configured.{Style.RESET_ALL}')
        remote_url = input(
            '🔗 Enter the remote repository URL (e.g., https://github.com/username/repo.git): '
        )

        # Add the remote repository as 'origin'
        subprocess.run(['git', 'remote', 'add', 'origin', remote_url])
        print(
            f'{Fore.GREEN}✅ Remote repository added as origin: {remote_url}{Style.RESET_ALL}'
        )

    # Attempt to push with --set-upstream
    result = subprocess.run(
        ['git', 'push', '--set-upstream', 'origin', 'main'],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        if 'rejected' in result.stderr:
            print(f'{Fore.RED}Error: Push rejected.{Style.RESET_ALL}')
            print(result.stderr)
            # Ask the user if they want to pull the latest changes
            pull_choice = input(
                'Do you want to pull the latest changes from the remote? (y/n): '
            )
            if pull_choice.lower() == 'y':
                print(
                    f'{Fore.YELLOW}Fetching and merging changes from the remote...{Style.RESET_ALL}'
                )
                fetch_result = subprocess.run(
                    ['git', 'fetch', 'origin'], capture_output=True, text=True
                )
                merge_result = subprocess.run(
                    ['git', 'merge', 'origin/main'],
                    capture_output=True,
                    text=True,
                )

                # Check for merge errors
                if merge_result.returncode != 0:
                    print(f'{Fore.RED}Error during merge: {Style.RESET_ALL}')
                    print(merge_result.stderr)
                    return

                # Try pushing again
                push_result = subprocess.run(['git', 'push', 'origin', 'main'])
                check_error(push_result)

            else:
                print(
                    f'{Fore.YELLOW}You chose not to pull changes. Please resolve the conflict manually.{Style.RESET_ALL}'
                )
        else:
            check_error(result)


def remove_submodule(org_repo):
    repo_path = f'repos/{org_repo}'
    if not os.path.isdir(repo_path):
        print(
            f"{Fore.RED}Error: Repository '{repo_path}' does not exist as a submodule.{Style.RESET_ALL}"
        )
        exit(1)

    print(
        f"{Fore.YELLOW}🗑 Removing submodule '{org_repo}'...{Style.RESET_ALL}"
    )
    subprocess.run(
        [
            'git',
            'config',
            '--file',
            '.gitmodules',
            '--remove-section',
            f'submodule.{repo_path}',
        ]
    )
    subprocess.run(
        ['git', 'config', '--remove-section', f'submodule.{repo_path}']
    )
    subprocess.run(['git', 'rm', '--cached', repo_path])
    os.system(f'rm -rf {repo_path}')
    subprocess.run(['git', 'add', '.gitmodules'])
    subprocess.run(['git', 'commit', '-m', f'Remove submodule {org_repo}'])
    print(
        f"{Fore.GREEN}✅ Submodule '{org_repo}' removed successfully.{Style.RESET_ALL}"
    )


def commit_all_changes():
    print(
        f'{Fore.GREEN}💾 Committing changes in both the main project and all submodules...{Style.RESET_ALL}'
    )
    commit_main_project()

    changes_found = False
    repos_with_changes = []

    # Check for changes in each submodule
    result = subprocess.run(
        [
            'git',
            'submodule',
            'foreach',
            '--recursive',
            'git status --porcelain',
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0 and result.stdout.strip():
        changes_found = True
        repos_with_changes = [line for line in result.stdout.splitlines()]

    if changes_found:
        print(f'{Fore.YELLOW}Repositories with changes:{Style.RESET_ALL}')
        for repo in repos_with_changes:
            print(f'- {repo}')

        commit_message = input('✏️ Enter commit message for submodules: ')
        subprocess.run(
            [
                'git',
                'submodule',
                'foreach',
                '--recursive',
                f"git add . && git commit -m '{commit_message}'",
            ]
        )
        check_error(result)
    else:
        print(
            f'{Fore.GREEN}✅ No changes found in submodules.{Style.RESET_ALL}'
        )


def push_all_changes():
    print(
        f'{Fore.GREEN}🔥 Pushing all changes (submodules and main project)...{Style.RESET_ALL}'
    )
    push_submodule_changes()
    push_main_project()
