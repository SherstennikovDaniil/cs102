import hashlib
import os
import pathlib
import re
import stat
import typing as tp
import zlib

from pyvcs.refs import update_ref
from pyvcs.repo import repo_find


def hash_object(data: bytes, fmt: str, write: bool = False) -> str:
    """
    Hash an object and return the hash (write to a file if write is set)
    """
    header = f"{fmt} {len(data)}\0".encode()
    store = header + data
    obj_hash = hashlib.sha1(store).hexdigest()
    obj = zlib.compress(store)
    if write:
        gitdir = repo_find()
        obj_dir = pathlib.Path(str(gitdir) + "/objects/" + obj_hash[:2])
        if not obj_dir.is_dir():
            os.makedirs(obj_dir)
        obj_name = obj_dir / obj_hash[2:]
        with open(obj_name, "wb") as obj_file:
            obj_file.write(obj)
    return obj_hash


def resolve_object(obj_name: str, gitdir: pathlib.Path) -> tp.List[str]:
    """
    Return objects by a prefix
    """
    if not 4 <= len(obj_name) <= 40:
        raise Exception(f"Not a valid object name {obj_name}")
    dir_name = obj_name[:2]
    obj_file = obj_name[2:]
    obj_dir = str(gitdir) + "/objects/" + dir_name
    files_list = os.listdir(obj_dir)
    objs = []
    for obj in files_list:
        if obj[: len(obj_file)] == obj_file:
            objs.append(dir_name + obj)

    if not objs:
        raise Exception(f"Not a valid object name {obj_name}")

    return objs


def find_object(obj_name: str, gitdir: pathlib.Path) -> str:
    """
    Not required, but might be useful
    """
    dir_name = obj_name[:2]
    file_name = obj_name[2:]
    path = str(gitdir) + os.sep + dir_name + os.sep + file_name
    return path


def read_object(sha: str, gitdir: pathlib.Path) -> tp.Tuple[str, bytes]:
    """
    Return object content
    """
    obj_name = resolve_object(sha, gitdir)[0]
    assert len(resolve_object(sha, gitdir)) == 1
    obj_dir = pathlib.Path(obj_name[:2])
    obj_file_name = pathlib.Path(obj_name[2:])
    path = gitdir / "objects" / obj_dir / obj_file_name
    with open(path, "rb") as obj_file:
        data = zlib.decompress(obj_file.read())
    newline_pos = data.find(b"\x00")
    header = data[:newline_pos]
    space_pos = header.find(b" ")
    obj_type = header[:space_pos].decode("ascii")
    content_len = int(header[space_pos:newline_pos].decode("ascii"))
    content = data[newline_pos + 1 :]
    assert content_len == len(content)
    return (obj_type, content)


def read_tree(data: bytes) -> tp.List[tp.Tuple[int, str, str]]:
    """
    Read a tree
    """
    tree_entries: tp.List[tp.Tuple[int, str, str]] = []
    while len(data) != 0:
        sha = bytes.hex(data[-20:])
        data = data[:-21]
        obj_type, _ = read_object(sha, repo_find())
        space_pos = data.rfind(b" ")
        name = data[space_pos + 1 :].decode("ascii")
        data = data[:space_pos]
        if obj_type == "tree":
            mode = "40000"
        else:
            mode = data[-6:].decode("ascii")
        mode_len = -1 * len(mode)
        data = data[:mode_len]
        mode_int = int(mode)
        tree_entries.insert(0, (mode_int, sha, name))
    return tree_entries


def cat_file(obj_name: str, pretty: bool = True) -> None:
    """
    Print file content by hash
    """
    gitdir = repo_find()
    obj_type, content = read_object(obj_name, gitdir)
    if obj_type == "blob":
        if pretty:
            result = content.decode("ascii")
            print(result)
        else:
            result = str(content)
            print(result)
    elif obj_type == "tree":
        tree_entries = read_tree(content)
        result = ""
        for entry in tree_entries:
            mode = str(entry[0])
            if len(mode) != 6:
                mode = "0" + mode
            tree_pointer_type, _ = read_object(entry[1], gitdir)
            print(f"{mode} {tree_pointer_type} {entry[1]}\t{entry[2]}")
    else:  # no tags supported
        _, content = read_object(resolve_object(obj_name, repo_find())[0], repo_find())
        print(content.decode())


def find_tree_files(
    tree_sha: str, gitdir: pathlib.Path, accumulator: str = ""
) -> tp.List[tp.Tuple[str, str]]:
    """
    Correlate tree to files
    """
    tree_files = []
    _, tree = read_object(tree_sha, gitdir)
    tree_entries = read_tree(tree)
    for entry in tree_entries:
        pointer_type, _ = read_object(entry[1], gitdir)
        path = pathlib.Path(entry[2]).relative_to(gitdir.parent)
        if path.is_dir():
            accumulator += str(path) + os.sep
        if pointer_type == "tree":
            tree_files += find_tree_files(entry[1], gitdir, accumulator)
        else:
            tree_files.append((entry[1], accumulator + str(path)))
    return tree_files


def commit_parse(raw: bytes, start: int = 0, dct=None):
    """
    Get the sha of a tree the commit is pointing to (stub)
    """
    data = raw.decode("ascii")
    data = data[5:]
    author_pos = data.find("author")
    tree = data[: author_pos - 2]
    return tree