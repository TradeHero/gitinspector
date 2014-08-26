#!/usr/bin/python
# coding: utf-8
#
# Copyright © 2012-2014 Ejwa Software. All rights reserved.
#
# This file is part of gitinspector.
#
# gitinspector is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# gitinspector is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with gitinspector. If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function
from __future__ import unicode_literals

import localization

localization.init()

import basedir
import format
import os
import sys
import terminal
import procedure
import subprocess

class Runner:
    def __init__(self):
        self.repo = "."
        self.command_line = "python " + " ".join(sys.argv[:])
        self.command_line = self.command_line.replace("main.py", "gitinspector.py")

    def output(self):
        terminal.skip_escapes(not sys.stdout.isatty())
        terminal.set_stdout_encoding()
        previous_directory = os.getcwd()

        os.chdir(self.repo)
        absolute_path = basedir.get_basedir_git()
        os.chdir(absolute_path)

        procedure.remove_inspection_branches()
        procedure.create_branches_for_inspection()

        format.output_header()

        sorted_branches = procedure.sort_branches_by_last_update()

        for (commit, branch_name) in sorted_branches:
            if procedure.eligible_for_inspection(commit):
                if procedure.switch_to_branch(branch_name):
                    output = subprocess.Popen(self.command_line, shell=True, bufsize=1, stdout=subprocess.PIPE).stdout
                    print(output.read())
            else:
                print("\n\n ==> All eligible branches have been inspected!")
                break

        procedure.remove_inspection_branches()
        os.chdir(previous_directory)

def __check_python_version__():
    if sys.version_info < (2, 6):
        python_version = str(sys.version_info[0]) + "." + str(sys.version_info[1])
        sys.exit(_("gitinspector requires at least Python 2.6 to run (version {0} was found).").format(python_version))


def main():
    terminal.check_terminal_encoding()
    terminal.set_stdin_encoding()
    __run__ = Runner()

    __check_python_version__()
    __run__.output()


if __name__ == "__main__":
    main()
