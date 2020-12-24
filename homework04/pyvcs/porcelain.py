import os
import pathlib
import shutil
import typing as tp

from pyvcs.index import read_index, update_index
from pyvcs.objects import commit_parse, find_object, find_tree_files, read_object
from pyvcs.refs import get_ref, is_detached, resolve_head, update_ref
from pyvcs.tree import commit_tree, write_tree


def add(gitdir: pathlib.Path, paths: tp.List[pathlib.Path]) -> None:
    """
    Update the current index
    """
    update_index(gitdir, paths, write=True)


def commit(gitdir: pathlib.Path, message: str, author: tp.Optional[str] = None) -> str:
    """
    Make a commit
    """
    tree = write_tree(gitdir, read_index(gitdir))
    return commit_tree(gitdir, tree, message, parent=None, author=author)


def checkout(gitdir: pathlib.Path, obj_name: str) -> None:
    """
    Checkout a new branch
    """
    update_ref(gitdir, "HEAD", obj_name)
    index_names = [entry.name for entry in read_index(gitdir)]
    _, commit_data = read_object(obj_name, gitdir)
    tree_hash = commit_parse(commit_data)
    files = find_tree_files(tree_hash, gitdir)
    to_be_updated = [pathlib.Path(i[1]) for i in files]
    update_index(gitdir, to_be_updated, write=True)
    for name in index_names:
        nodes = name.split(os.sep)
        if pathlib.Path(nodes[0]).is_dir():
            shutil.rmtree(nodes[0])
        else:
            if pathlib.Path(nodes[0]).exists():
                os.remove(nodes[0])
    for sha, name in files:
        if name.find(os.sep) != -1:
            prefix, _ = os.path.split(name)
            if not pathlib.Path(prefix).exists():
                os.makedirs(prefix)
        _, content = read_object(sha, gitdir)
        with open(name, "wb") as file_obj:
            file_obj.write(content)