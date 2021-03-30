#
# Part of mpygit - demo/history.py -
#  Simple demonstration program, it implemenets (roughly) what git log does
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

import argparse
import datetime
import mpygit
import gitutil

parser = argparse.ArgumentParser(description="git log using mpygit")
parser.add_argument("path", default=".", nargs='?',
                    help="Path to repository")
parser.add_argument("--start", "-s",
                    help="Where to start walking the history from")
parser.add_argument("--num", "-n",
                    type=int, default=100, help="Number of commits to display")
args = parser.parse_args()

# Open a repository in the current directory
repo = mpygit.Repository(args.path)
start_oid = repo.HEAD if args.start is None else args.start

def fmtdatetime(unixtime):
    ts = datetime.datetime.utcfromtimestamp(unixtime)
    return ts.strftime("%Y-%m-%d %H:%M:%S")

def printmsg(msg, indent=4):
    print()
    for line in msg.split("\n"):
        print(" " * indent + line)
    print()

for commit in gitutil.walk(repo, start_oid, args.num):
    print("commit " + commit.oid)
    print("Author:", commit.author)
    print("Date:", fmtdatetime(commit.author.timestamp), commit.author.tz)
    printmsg(commit.message)
