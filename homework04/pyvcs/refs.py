import pathlib
import typing as tp


def update_ref(gitdir: pathlib.Path, ref: tp.Union[str, pathlib.Path], new_value: str) -> None:
    """
    Set new value to a ref
    """
    with open(pathlib.Path(gitdir / ref), "w") as ref_file:
        ref_file.write(new_value)


def symbolic_ref(gitdir: pathlib.Path, name: str, ref: str) -> None:
    """
    Define a symbolic ref
    """
    with open(gitdir / name, "w") as ref_file:
        ref_file.write(ref)


def ref_resolve(gitdir: pathlib.Path, refname: str) -> str:
    """
    Get the hash of a commit the ref is pointing to
    """
    if refname == "HEAD":
        refname = get_ref(gitdir)
    if is_detached(gitdir):
        return refname
    with open(gitdir / pathlib.Path(refname), "r") as ref:
        data = ref.read()
    return data


def resolve_head(gitdir: pathlib.Path) -> tp.Optional[str]:
    """
    Get the current HEAD state
    """
    refname = get_ref(gitdir)
    if not (gitdir / pathlib.Path(refname)).exists():
        return None
    with open(gitdir / pathlib.Path(refname), "r") as ref:
        data = ref.read()
    return data


def is_detached(gitdir: pathlib.Path) -> bool:
    """
    Is the repo decapitated (I'm joking, okay?)
    """
    with open(gitdir / "HEAD", "r") as head:
        data = head.read()
    if data[:3] == "ref":
        return False

    return True


def get_ref(gitdir: pathlib.Path) -> str:
    """
    Get the commit ref or commit the HEAD points to
    """
    with open(gitdir / "HEAD", "r") as head:
        if not is_detached(gitdir):
            refname = head.read()[5:-1]
        else:
            refname = head.read()
    return refname
