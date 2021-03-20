import configparser
from pathlib import Path
import re
import zlib

class Blob:
    def __init__(self, data):
        self.data = data

class Tree:
    def __init__(self, data):
        pass

class CommitStamp:
    def __init__(self, val):
        # Parse commit stamp
        m = re.match(r"([\s\S]*) \<([\s\S]*)\> ([\s\S]*) ([\s\S]*)", val)
        # Make sure the format was correct
        assert m != None

        self.name, self.email, self.timestamp, self.tz = \
            m.group(1), m.group(2), m.group(3), m.group(4)

        def __repr__(self):
            return f"{self.name} <{self.email}> {self.timestamp} {self.tz}"
        def __str__(self):
            return repr(self)

class Commit:
    def __init__(self, data):
        data_str = data.decode()
        lines = data_str.split("\n")
        for i, line in enumerate(lines):
            if line == "": # blank line for commit msg
                self.message = "\n".join(lines[i+1:])
                break
            key, val = line.split(" ", 1)
            if key == "tree":
                self.tree = val
            elif key == "author":
                self.author = CommitStamp(val)
            elif key == "committer":
                self.committer = CommitStamp(val)
    def __repr__(self):
        pass
    def __str__(self):
        return repr(self)

class Repository:
    def __init__(self, path):
        self.path = Path(path)

    @property
    def config(self):
        config = configparser.ConfigParser()
        config.read(self.path / "config")
        return config

    @property
    def tags(self):
        """List of tags"""
        return { ref.name : ref.read_text().strip()
                 for ref in (self.path / "refs" / "tags").iterdir() }

    @property
    def heads(self):
        """List of heads (aka branches)"""
        return { ref.name : ref.read_text().strip()
                 for ref in (self.path / "refs" / "heads").iterdir() }

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
        obj_hdr, obj_data = zlib.decompress(obj_path.read_bytes()).split(b"\x00")
        obj_type, obj_size = obj_hdr.split(b" ")
        if obj_type == b"blob":
            return Blob(obj_data)
        elif obj_type == b"tree":
            return Commit(obj_data)
        elif obj_type == b"commit":
            return Commit(obj_data)
        return None


repo = Repository(".git")
c = repo[repo.heads["master"]]

