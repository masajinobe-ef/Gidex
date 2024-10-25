import os

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.join(PROJECT_DIR, '..', 'repos')
MAX_CONCURRENT_DOWNLOADS = 4

# Constants
BRANCH_NAME = 'main'
SUBMODULES_DIR = 'repos'
GITMODULES_FILE = '.gitmodules'
