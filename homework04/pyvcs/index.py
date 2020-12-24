import hashlib
import os
import pathlib
import string
import struct
import typing as tp

from pyvcs.objects import hash_object


class GitIndexEntry(tp.NamedTuple):
    """
    An index entry in readable format
    """
    ctime_s: int
    ctime_n: int
    mtime_s: int
    mtime_n: int
    dev: int
    ino: int
    mode: int
    uid: int
    gid: int
    size: int
    sha1: bytes
    flags: int
    name: str

    def pack(self) -> bytes:
        """
        Pack into index format
        """
        values = (
            self.ctime_s,
            self.ctime_n,
            self.mtime_s,
            self.mtime_n,
            self.dev,
            self.ino & 0xFFFFFFFF,
            self.mode,
            self.uid,
            self.gid,
            self.size,
            self.sha1,
            self.flags,
        )
        bytecast_str = struct.pack("!LLLLLLLLLL20sH", *values)  # pack
        bytecast_str += self.name.encode("ascii")
        if not len(bytecast_str) % 8 == 0:
            padding_size = 8 - (len(bytecast_str) % 8)
            for _ in range(0, padding_size):
                bytecast_str += b"\x00"
        return bytecast_str

    @staticmethod
    def unpack(data: bytes) -> "GitIndexEntry":
        """
        Unpack into readable format
        """
        last_byte = data[-1]
        while last_byte == 0:
            data = data[:-1]
            last_byte = data[-1]
        name = ""
        while chr(last_byte) in (
            string.ascii_letters + string.punctuation + string.digits
        ):
            name += chr(last_byte)
            data = data[:-1]
            last_byte = data[-1]
        name = name[::-1]
        unpacked = struct.unpack("!LLLLLLLLLL20sH", data)
        index_entry = GitIndexEntry(
            unpacked[0],
            unpacked[1],
            unpacked[2],
            unpacked[3],
            unpacked[4],
            unpacked[5],
            unpacked[6],
            unpacked[7],
            unpacked[8],
            unpacked[9],
            unpacked[10],
            unpacked[11],
            name,
        )
        return index_entry


def read_index(gitdir: pathlib.Path) -> tp.List[GitIndexEntry]:
    """
    Get index entries in readable format from index
    """
    index_entries = []
    if not (gitdir / "index").is_file():
        return []
    with open(gitdir / "index", "rb") as index_file:
        data = index_file.read()
    entry_count = struct.unpack("!i", data[8:12])[0]
    data = data[12:]
    for _ in range(entry_count):
        entry = data[:60]
        flags = data[60:62]
        data = data[62:]
        entry += flags
        num_flags = int.from_bytes(flags, "big")
        name = data[:num_flags].decode()
        data = data[num_flags:]
        entry += name.encode()
        while True:
            if len(data) == 0:
                break
            byte = chr(data[0])
            if byte != "\x00":
                break
            entry += byte.encode("ascii")
            data = data[1:]

        entry_unpacked = GitIndexEntry.unpack(entry)
        index_entries.append(entry_unpacked)

    return index_entries


def write_index(gitdir: pathlib.Path, entries: tp.List[GitIndexEntry]) -> None:
    """
    Write entries to index
    """
    with open(gitdir / "index", "wb") as index_file:
        version = 2
        version_bytecast = version.to_bytes(4, "big")
        entries_len_bytecast = len(entries).to_bytes(4, "big")
        index_content = "DIRC".encode()
        index_content += version_bytecast
        index_content += entries_len_bytecast
        for entry in entries:
            index_content += entry.pack()
        index_sha = hashlib.sha1(index_content).digest()
        index_content += index_sha
        index_file.write(index_content)


def ls_files(gitdir: pathlib.Path, details: bool = False) -> None:
    """
    Get indexed files' details
    """
    index_entries = read_index(gitdir)
    if details:
        for entry in index_entries:
            mode = str(oct(entry.mode))[
                2:
            ]
            sha = entry.sha1.hex()
            stage = (entry.flags >> 12) & 3
            print(f"{mode} {sha} {stage}\t{entry.name}")
    else:
        for entry in index_entries:
            print(f"{entry.name}")


def update_index(gitdir: pathlib.Path, paths: tp.List[pathlib.Path], write: bool = True) -> None:
    """
    Update index by adding new files
    """
    index_entries: tp.List[GitIndexEntry] = []
    absolute_paths = [i.absolute() for i in paths]
    absolute_paths.sort()
    relative_paths = [
        i.relative_to(os.getcwd()) for i in absolute_paths
    ]
    relative_paths.reverse()
    for path in relative_paths:
        with open(path, "rb") as f_name:
            data = f_name.read()
        obj_hash = bytes.fromhex(hash_object(data, "blob", True))
        os_stats = os.stat(path, follow_symlinks=False)
        name_len = len(str(path))
        if name_len > 0xFFF:
            name_len = 0xFFF
        flags = name_len
        index_entry = GitIndexEntry(
            int(os_stats.st_ctime),
            0,
            int(os_stats.st_mtime),
            0,
            os_stats.st_dev,
            os_stats.st_ino,
            os_stats.st_mode,
            os_stats.st_uid,
            os_stats.st_gid,
            os_stats.st_size,
            obj_hash,
            flags,
            str(path),
        )
        if index_entry not in index_entries:
            index_entries.insert(0, index_entry)

    if write:
        write_index(gitdir, index_entries)