# Gidex

Gidex is a command-line tool designed for synchronizing GitHub repositories as submodules within a local repository. This is particularly useful for managing dependencies and collaborating across multiple projects within specified organizations.

## Installation

To install Gidex, follow these steps:

```sh
$ git clone https://github.com/masajinobe-ef/gidex.git --depth=1
$ cd gidex
$ sudo chmod +x sync.sh
$ ./sync.sh
```

Edit the orgs.toml file to specify the organizations whose repositories you want to synchronize.

## Command Reference

| Command                          | Description                                                       |
|----------------------------------|-------------------------------------------------------------------|
| `./sync.sh --update`           | Update all submodules to the latest commits from remote repositories. |
| `./sync.sh --commit`           | Commit changes in submodules. You will be prompted for a commit message. |
| `./sync.sh --push`             | Push changes to remote repositories of submodules.               |
| `./sync.sh --main-commit`      | Commit changes in the Gidex project. You will be prompted for a commit message. |
| `./sync.sh --all-push`         | Push all changes (submodules and main project) to remote repositories. |
| `./sync.sh --help`             | Show help information about available commands.                  |

## License

Gidex is licensed under the GPL-3.0 License. You can view the full license text in the LICENSE file in the repository.
