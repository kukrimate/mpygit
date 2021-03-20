# Read only, pure Python git implementation
# Author: Mate Kukri

import binascii
import configparser
import pathlib
import re
import zlib

class Blob:
    def __init__(self, data):
        self.data = data

class TreeEntry:
    def __init__(self, name, mode, oid):
        self.name = name
        self.mode = mode
        self.oid = oid

    def __repr__(self):
        return f"({self.name}  {self.mode} {self.oid})"

class Tree:
    def __init__(self, data):
        self.entries = []

        while len(data) > 0:
            meta, rest = data.split(b"\x00", 1)
            meta = meta.decode()
            mode, name = meta.split(" ", 1)
            self.entries.append(
                TreeEntry(name, mode, binascii.hexlify(rest[:20]).decode()))
            data = rest[20:]

    def __repr__(self):
        return f"Tree{repr(self.entries)}"

class CommitStamp:
    def __init__(self, val):
        # Parse commit stamp
        m = re.match(r"([\s\S]*) \<([\s\S]*)\> ([\s\S]*) ([\s\S]*)", val)
        # Make sure the format was correct
        assert m != None
        self.name, self.email, self.timestamp, self.tz = \
            m.group(1), m.group(2), m.group(3), m.group(4)

    def __repr__(self):
        return f"{self.name} <{self.email}>"

class Commit:
    def __init__(self, data):
        data_str = data.decode()
        lines = data_str.split("\n")
        if lines[-1] == "":
            lines.pop(-1)

        # Create list for parent commits
        self.parents = []

        # Parse metadata
        for i, line in enumerate(lines):
            if line == "":
                self.message = "\n".join(lines[i+1:])
                break

            key, val = line.split(" ", 1)
            if key == "tree":
                self.tree = val
            elif key == "parent":
                self.parents.append(val)
            elif key == "author":
                self.author = CommitStamp(val)
            elif key == "committer":
                self.committer = CommitStamp(val)

    def __repr__(self):
        return f"{self.author} {self.message}"

class Repository:
    def __init__(self, path):
        self.path = pathlib.Path(path)

    @property
    def config(self):
        config = configparser.ConfigParser()
        config.read(self.path / "config")
        return config

    def _read_packed_refs(self, tgt_dict, want):
        packed_refs_path = self.path / "packed-refs"

        # Return if packed references file is empty
        if not packed_refs_path.exists():
            return

        for line in packed_refs_path.read_text().split("\n"):
            # Skip empty lines and comments
            if line == "" or line[0] == "#":
                continue

            # Add packed reference if desired
            val, key = line.split(" ", 1)
            if key.startswith(want):
                tgt_dict[key[len(want):]] = val

    @property
    def tags(self):
        """List of tags"""
        tags = { ref.name : ref.read_text().strip()
                 for ref in (self.path / "refs" / "tags").iterdir() }
        self._read_packed_refs(tags, "refs/tags/")
        return tags

    @property
    def heads(self):
        """List of heads (aka branches)"""
        heads = { ref.name : ref.read_text().strip()
                 for ref in (self.path / "refs" / "heads").iterdir() }
        self._read_packed_refs(heads, "refs/heads/")
        return heads

    @property
    def HEAD(self):
        """Global head"""

        # Please note that this is a symbolic reference so it might contain
        # either an object ID, or a pointer to an actual reference
        sym_ref = (self.path / "HEAD").read_text()

        m = re.match(r"ref:\s*(\S*)", sym_ref)
        if m != None:
            return m.group(1)
        else:
            return sym_ref

    def __getitem__(self, key):
        """Lookup an object ID in the repository"""
        obj_path = self.path / "objects" / key[:2] / key[2:]
        obj_hdr, obj_data = zlib.decompress(obj_path.read_bytes()).split(b"\x00", 1)
        obj_type, obj_size = obj_hdr.split(b" ")

        if obj_type == b"blob":
            return Blob(obj_data)
        elif obj_type == b"tree":
            return Tree(obj_data)
        elif obj_type == b"commit":
            return Commit(obj_data)

        return None


repo = Repository(".git")
print(repo.heads)
c = repo[repo.heads["master"]]
print(c.tree)
t = repo[c.tree]
print(t)
