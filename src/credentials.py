import os


def load_credentials() -> tuple:
    with open(os.path.expanduser('~/.git-credentials')) as f:
        credentials = f.read().strip()
    username = credentials.split('/')[2].split(':')[0]
    token = credentials.split('@')[0].split(':')[1]
    return username, token
