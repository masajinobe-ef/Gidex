import os
import toml
from constants import PROJECT_DIR


def load_org_names() -> list:
    with open(os.path.join(PROJECT_DIR, '../orgs.toml'), 'r') as toml_file:
        data = toml.load(toml_file)
        return data.get('orgs', [])
