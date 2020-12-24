import os
import pathlib
import typing as tp


def repo_find(workdir: tp.Union[str, pathlib.Path] = ".") -> pathlib.Path:
    """
    Find a .GIT_DIR directory in a repo, throw an Exception if none found
    """
    path = pathlib.Path(workdir)
    del workdir
    gitdir_name = os.getenv("GIT_DIR")
    if not gitdir_name:
        gitdir_name = ".git"
    gitdir = path / gitdir_name
    for parent in gitdir.parents:
        prefix, _ = os.path.split(parent)
        if str(parent) == prefix + f"/{gitdir_name}":
            gitdir = pathlib.Path(prefix + f"/{gitdir_name}")
    if gitdir.exists():
        return gitdir.absolute()

    raise Exception("Not a git repository")


def repo_create(workdir: tp.Union[str, pathlib.Path]) -> pathlib.Path:
    """
    Create a basic git repo structure
    """
    path = pathlib.Path(workdir)
    del workdir
    if not path.is_dir():
        raise Exception(f"{path} is not a directory")
    gitdir_name = os.getenv("GIT_DIR")
    if not gitdir_name:
        gitdir_name = ".git"
    gitdir = path / gitdir_name
    if not gitdir.is_dir():
        os.makedirs(gitdir)
        os.makedirs(str(gitdir) + "/refs/heads")
        os.makedirs(str(gitdir) + "/refs/tags")
        os.makedirs(str(gitdir) + "/objects")
        with open(gitdir / "HEAD", "w") as head:
            head.write("ref: refs/heads/master\n")
        with open(gitdir / "config", "w") as config:
            config.write(
                "[core]\n\trepositoryformatversion = 0\n\tfilemode = true\n\tbare = false\n\tlogallrefupdates = false\n"
            )
        with open(gitdir / "description", "w") as description:
            description.write("Unnamed pyvcs repository.\n")

    return gitdir