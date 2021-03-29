#
# Simple demonstration program for mpygit,
# it implemenets (roughly) what git log does
#

import argparse
import datetime
import mpygit
import sys

parser = argparse.ArgumentParser(description="git log using mpygit")
parser.add_argument("--start", help="Where to start walking the history from")
parser.add_argument("--depth", type=int, default=100, help="How far to walk up the history")
parser.add_argument("path", default=".", nargs='?', help="Path to repository")
args = parser.parse_args()

# Open a repository in the current directory
repo = mpygit.Repository(args.path)
start = repo.HEAD if args.start is None else args.start
cnt = args.depth

def fmtdatetime(unixtime):
    ts = datetime.datetime.utcfromtimestamp(unixtime)
    return ts.strftime("%Y-%m-%d %H:%M:%S")

def printmsg(msg, indent=4):
    print()
    for line in msg.split("\n"):
        print(" " * indent + line)
    print()

# Walk history
parents = [ start ]
visited = set()

while cnt > 0 and len(parents) > 0:
    oid = parents.pop()
    if oid in visited:
        continue
    parents += repo[oid].parents
    visited.add(oid)
    cnt -= 1

# Print commits sorted
for oid in sorted(visited, reverse=True):
    print("commit " + (oid if len(oid) == 40 else repo.heads[oid] + f" ({oid})"))
    commit = repo[oid]
    print("Author:", commit.committer)
    print("Date:", fmtdatetime(commit.committer.timestamp), commit.committer.tz)
    printmsg(commit.message)
