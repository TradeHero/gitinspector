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
import getopt
from datetime import date, timedelta
import subprocess

import filtering
import localization
import optval


localization.init()

import basedir
import format
import os
import sys
import terminal


class Runner:
    def __init__(self):
        self.repo = "."
        self.command_line = "python " + " ".join(sys.argv[:])
        self.command_line = self.command_line.replace("multiple.py", "main.py")
        self.weeks = 3

    def output(self):
        terminal.skip_escapes(not sys.stdout.isatty())
        terminal.set_stdout_encoding()

        os.chdir(self.repo)
        absolute_path = basedir.get_basedir_git()
        os.chdir(absolute_path)

        today = date.today()
        offset = today.weekday() % 7 + 1
        this_sunday = today - timedelta(days = offset)
        self.render_report(this_sunday, today)

        for i in range(1, self.weeks + 1):
            since = this_sunday - timedelta(days = i * 7)
            until = since + timedelta(days = 7)
            self.render_report(since, until)


    def render_report(self, since, until):
        output = subprocess.Popen(self.command_line + " --since={0} --until={1}".format(since, until), shell=True, bufsize=1, stdout=subprocess.PIPE).stdout
        output = output.read()
        print(output)


    def set_weeks_to_inspect(self, token):
        self.weeks = int(token)

def __check_python_version__():
    if sys.version_info < (2, 6):
        python_version = str(sys.version_info[0]) + "." + str(sys.version_info[1])
        sys.exit(_("gitinspector requires at least Python 2.6 to run (version {0} was found).").format(python_version))


def main():
    terminal.check_terminal_encoding()
    terminal.set_stdin_encoding()
    argv = terminal.convert_command_line_to_utf8()

    __run__ = Runner()

    try:
        __opts__, __args__ = optval.gnu_getopt(argv[1:], "f:F:hHlLmrTwx:", ["exclude=", "file-types=", "format=",
                                                                            "hard:true", "help", "list-file-types:true",
                                                                            "localize-output:true", "metrics:true",
                                                                            "responsibilities:true",
                                                                            "since=", "grading:true", "timeline:true",
                                                                            "until=", "version",
                                                                            "ws="])
        for arg in __args__:
            __run__.repo = arg

        for o, a in __opts__:
            if o == "--ws":
                __run__.set_weeks_to_inspect(a)

        __check_python_version__()
        __run__.output()
    except (
        filtering.InvalidRegExpError, format.InvalidFormatError, optval.InvalidOptionArgument, getopt.error) as exception:
        print(sys.argv[0], "\b:", exception.msg, file=sys.stderr)
        print(_("Try `{0} --help' for more information.").format(sys.argv[0]), file=sys.stderr)
        sys.exit(2)

if __name__ == "__main__":
    main()
