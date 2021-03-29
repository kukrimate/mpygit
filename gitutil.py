#
# Part of mpygit - gitutil.py - Additional utility functions
#
# Copyright (C) 2021  Mate Kukri
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

import difflib

def diff_commits(repo, commit1, commit2):
    """Generate diffs between two commits in a repository"""
    diffs = []

    def added_blob(path, blob):
        if blob.is_binary:
            diffs.append(("/".join(path), "Binary file added", "A"))
        else:
            patch = "".join(
                difflib.unified_diff(
                    [],
                    blob.text.splitlines(keepends=True),
                    "/dev/null",
                    "/".join(["b"] + path),
                )
            )
            diffs.append(("/".join(path), patch, "A"))

    def modified_blob(path, blob1, blob2):
        if blob1.is_binary or blob2.is_binary:
            diffs.append(("/".join(path), "Binary file modified", "M"))
        else:
            patch = "".join(
                difflib.unified_diff(
                    blob1.text.splitlines(keepends=True),
                    blob2.text.splitlines(keepends=True),
                    "/".join(["a"] + path),
                    "/".join(["b"] + path),
                )
            )
            diffs.append(("/".join(path), patch, "M"))

    def deleted_blob(path, blob):
        if blob.is_binary:
            diffs.append(("/".join(path), "Binary file deleted", "D"))
        else:
            patch = "".join(
                difflib.unified_diff(
                    blob.text.splitlines(keepends=True),
                    [],
                    "/".join(["a"] + path),
                    "/dev/null",
                )
            )
            diffs.append(("/".join(path), patch, "D"))

    def added_subtree(path, tree):
        for entry in tree:
            entry_path = path + [entry.name]
            if entry.isreg():
                added_blob(entry_path, repo[entry.oid])
            elif entry.isdir():
                added_subtree(entry_path, repo[entry.oid])

    def deleted_subtree(path, tree):
        for entry in tree:
            entry_path = path + [entry.name]
            if entry.isreg():
                deleted_blob(entry_path, repo[entry.oid])
            elif entry.isdir():
                deleted_subtree(entry_path, repo[entry.oid])

    def diff_subtree(path, tree1, tree2):
        for entry in tree1:  # Look for deleted blobs
            newent = tree2[entry.name]
            entry_path = path + [entry.name]
            if entry.isreg():
                if newent is None or not newent.isreg():
                    deleted_blob(entry_path, repo[entry.oid])
            elif entry.isdir():
                if newent is None or not newent.isdir():
                    deleted_subtree(entry_path, repo[entry.oid])

        for entry in tree2:  # Look for added or modified blobs
            oldent = tree1[entry.name]
            entry_path = path + [entry.name]
            if entry.isreg():
                if oldent is None or not oldent.isreg():
                    added_blob(entry_path, repo[entry.oid])
                elif entry.oid != oldent.oid:
                    modified_blob(entry_path, repo[oldent.oid], repo[entry.oid])
            elif entry.isdir():
                if oldent is None or not oldent.isdir():
                    added_subtree(entry_path, repo[entry.oid])
                elif entry.oid != oldent.oid:
                    diff_subtree(entry_path, repo[oldent.oid], repo[entry.oid])

    if commit1 is None:
        added_subtree([], repo[commit2.tree])
    else:
        diff_subtree([], repo[commit1.tree], repo[commit2.tree])
    return diffs
