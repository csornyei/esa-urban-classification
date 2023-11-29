import subprocess
from datetime import datetime
from pathlib import Path


def _git_checkout_branch(branch_name: str):
    subprocess.run(["git", "checkout", "-b", branch_name])


def _git_add(folder: str):
    subprocess.run(["git", "add", folder])


def _git_commit(message: str):
    subprocess.run(["git", "commit", "-m", message])


def _git_push():
    subprocess.run(["git", "push", "origin", "HEAD"])


def _dvc_add(folder: str):
    subprocess.run(["dvc", "add", folder])


def _dvc_push():
    subprocess.run(["dvc", "push"])


def load():
    data_folder = Path("./data")
    folders = [folder for folder in data_folder.iterdir() if folder.is_dir()]

    day = datetime.now().strftime("%Y-%m-%d")
    _git_checkout_branch(
        day + "-".join([folder.name for folder in folders]).replace(" ", "-")
    )

    for folder in folders:
        _dvc_add(str(folder))

        _git_add(str(folder) + ".dvc")

    _dvc_push()

    _git_commit(f"Add data for {day}")

    _git_push()


if __name__ == "__main__":
    load()
