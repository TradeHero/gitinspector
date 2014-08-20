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

import os
import subprocess
import sys


def get_basedir():
    if hasattr(sys, 'frozen'): # exists when running via py2exe
        return sys.prefix
    else:
        return os.path.dirname(os.path.realpath(__file__))


__git_basedir__ = None


def get_basedir_git():
    global __git_basedir__

    if not __git_basedir__:
        isbare = subprocess.Popen("git rev-parse --is-bare-repository", shell=True, bufsize=1,
                                  stdout=subprocess.PIPE).stdout
        isbare = isbare.readlines()
        isbare = (isbare[0].decode("utf-8", "replace").strip() == "true")
        absolute_path = ""

        if isbare:
            absolute_path = subprocess.Popen("git rev-parse --git-dir", shell=True, bufsize=1,
                                             stdout=subprocess.PIPE).stdout
        else:
            absolute_path = subprocess.Popen("git rev-parse --show-toplevel", shell=True, bufsize=1,
                                             stdout=subprocess.PIPE).stdout

        absolute_path = absolute_path.readlines()
        if len(absolute_path) == 0:
            sys.exit(_("Unable to determine absolute path of git repository."))

        __git_basedir__ = absolute_path[0].decode("utf-8", "replace").strip()

    return __git_basedir__
