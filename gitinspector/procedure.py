from __future__ import print_function
import os
import subprocess
import threading
import interval
import shelve

from datetime import datetime, date
from datetime import timedelta
from os.path import expanduser

HIDE_ERR_OUTPUT = " >/dev/null 2>&1"
COMMIT_LIST_FILE = expanduser("~/.gi_commit")
DB_FILE = expanduser("~/.gi_db")

DEBUG = False

__since_date_time__ = ""
__until_date_time__ = ""


def git_cleanup_and_reset():
    output = subprocess.Popen("git clean -fd && git reset HEAD --hard" + HIDE_ERR_OUTPUT,
                              shell=True, bufsize=1, stdout=subprocess.PIPE).stdout
    output.readlines()


def create_branches_for_inspection():
    debug_print("Cleaning current branch ...")
    git_cleanup_and_reset()

    switch_to_master_branch()

    debug_print("Fetch all branches ...")
    err_output = subprocess.Popen("git fetch --all --prune", shell=True, bufsize=1, stdout=subprocess.PIPE).stdout
    err_output.readlines()

    debug_print("Creating branches for inspection ...")
    command_line = "for remote in `git branch -r `; do" \
                   " if [[ $remote != *HEAD* && $remote == origin* ]]; then" \
                   " git checkout -b ${remote/origin\//insp\/} $remote;" \
                   " fi; done"
    process = \
        subprocess.Popen(command_line, shell=True, bufsize=1, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    process_stderr = process.stderr
    err_output = process_stderr.read()
    if ".lock" in err_output:
        print("\n\nPlease ensure that there is not another git process is running on the same repo!")
        print("Delete .git/index.lock file in the current folder and rerun the application again.")
        exit()


def switch_to_master_branch():
    debug_print("Switch back to master branch ...")
    output = subprocess.Popen("git checkout master" + HIDE_ERR_OUTPUT,
                              shell=True, bufsize=1, stdout=subprocess.PIPE).stdout
    output.readlines()


def remove_inspection_branches():
    switch_to_master_branch()

    debug_print("Removing all branches for inspection ...")
    output = subprocess.Popen("for remote in `git branch -r `; do git branch -D ${remote/origin\//insp\/}; done"
                              + HIDE_ERR_OUTPUT,
                              shell=True, bufsize=1, stdout=subprocess.PIPE).stdout
    output.readlines()


def get_commit_date(commit):
    output = \
        subprocess.Popen("git log -1 -s --format=%ci " + commit + " | cat",
                         shell=True, bufsize=1, stdout=subprocess.PIPE).stdout
    line = output.readline()
    return line


def sort_branches_by_last_update():
    debug_print("Sorting branches by last update time ...")
    output = \
        subprocess.Popen("git for-each-ref --sort=-committerdate refs/heads/|grep insp",
                         shell=True, bufsize=1, stdout=subprocess.PIPE).stdout
    lines = output.readlines()

    branch_commit_pairs = []
    for i in lines:
        j = i.strip().decode("unicode_escape", "ignore")
        j = j.encode("latin-1", "replace")
        j = j.decode("utf-8", "replace")

        (commit, branch_name) = j.rsplit(" commit\trefs/heads/")
        branch_commit_pairs.append((commit, branch_name))

    return branch_commit_pairs


def eligible_for_inspection(commit):
    global __since_date_time__
    global __until_date_time__

    __since_date_time__ = interval.get_since()
    if __since_date_time__:
        __since_date_time__ = __since_date_time__.split("=")
        __since_date_time__ = __since_date_time__[1]
        __since_date_time__ = __since_date_time__.replace("\"", "")
    else:
        __since_date_time__ = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    __since_date_time__ = __since_date_time__.strip()


    __until_date_time__ = interval.get_until()

    if __until_date_time__:
        __until_date_time__ = __until_date_time__.split("=")
        __until_date_time__ = __until_date_time__[1]
        __until_date_time__ = __until_date_time__.replace("\"", "")
    else:
        __until_date_time__ = datetime.now().strftime("%Y-%m-%d")

    __until_date_time__ = __until_date_time__.strip()

    return get_commit_date(commit) > __since_date_time__


def switch_to_branch(branch_name):
    git_cleanup_and_reset()

    debug_print("\n============ Inspecting " + branch_name)
    output = \
        subprocess.Popen("git checkout -f " + branch_name + HIDE_ERR_OUTPUT,
                         shell=True, bufsize=1, stdout=subprocess.PIPE).stdout
    lines = output.readlines()
    return True


def remove_commit_log():
    if os.path.isfile(COMMIT_LIST_FILE):
        os.remove(COMMIT_LIST_FILE)

def remove_temp_db():
    if os.path.isfile(DB_FILE):
        os.remove(DB_FILE)

def prepare_commit_log():
    remove_commit_log()


__processed_commits__ = []
__processed_commits_lock__ = threading.Lock()


def get_processed_commits():
    global __processed_commits__
    try:
        __processed_commits_lock__.acquire()
        if os.path.isfile(COMMIT_LIST_FILE) and len(__processed_commits__) == 0:
            with open(COMMIT_LIST_FILE, "rb") as f:
                __processed_commits__.extend(f.read().split('\n'))

        return __processed_commits__
    finally:
        __processed_commits_lock__.release()


def append_process_commit(commit):
    __processed_commits__.append(commit)
    with open(COMMIT_LIST_FILE, "a") as f:
        f.write(commit + "\n")


__report__ = {}


class Report:
    def __init__(self, string):
        report_line = string.split()

        if report_line.__len__() >= 3:
            self.commits = int(report_line[0])
            self.insertions = int(report_line[1])
            self.deletions = int(report_line[2])

    def to_array(self):
        return [self.commits, self.insertions, self.deletions]


# TODO following is a little hack to use subprocess output for gathering data
# TODO What we should do is to either find a proper way for communication between
# TODO parent and subprocess or merge the processes into only one
#
# Why the subprocess output is parsed like following? Check this method out ${link changes#output_text}
def process_branch_output(output):
    report_position = output.find("\nAuthor")
    if report_position >= 0:
        global __report__
        output = output[report_position:]
        lines = output.split('\n')
        # one line for the \n, another is the line with "Author"
        lines = lines[2:]
        for line in lines:
            author = line[:20].strip()
            if len(author) > 0:
                single_report = Report(line[20:])
                if __report__.has_key(author):
                    author_report = __report__[author]
                    author_report.commits += single_report.commits
                    author_report.insertions += single_report.insertions
                    author_report.deletions += single_report.deletions
                else:
                    __report__[author] = single_report


def output_final_report():
    print(_("Report from {0} to {1}".format(__since_date_time__, __until_date_time__)))
    print(_("Author").ljust(21) + "\t" + _("Commits").rjust(13) + "\t" + _("Insertions").rjust(14) + "\t" +
          _("Deletions").rjust(15))

    for author, report in __report__.iteritems():
        print(author.ljust(20)[0:20], end="\t")
        print(str(report.commits).rjust(13), end="\t")
        print(str(report.insertions).rjust(13), end="\t")
        print(str(report.deletions).rjust(14), end="\t")
        print("\n".rstrip())

        db = shelve.open(DB_FILE)

        if db.has_key(author):
            author_table = db[author]
            author_table[__since_date_time__] = report.to_array()
            db[author] = author_table
        else:
            db[author] = {__since_date_time__: report.to_array()}
        db.close()


def output_to_db():
    db = shelve.open(DB_FILE)
    for author, report in __report__.iteritems():

        if db.has_key(author):
            author_table = db[author]
            author_table[__since_date_time__] = report.to_array()
            db[author] = author_table
        else:
            db[author] = {__since_date_time__: report.to_array()}
    db.close()


def format_statistic(commits, insertions, deletions, net):
    return net.rjust(16) + "\t||\t"
    # return commits.rjust(13) + "\t" + insertions.rjust(14) + "\t" + deletions.rjust(15) + "\t" + net.rjust(16) + "\t||\t"

def format_header(title1, title2, title3, title4 = ""):
    return title4.rjust(16) + "\t||\t"
    # return title1.rjust(13) + "\t" + title2.rjust(14) + "\t" + title3.rjust(15) + "\t" + title4.rjust(16) + "\t||\t"


def output_final_report_in_one_block(ws):
    today = date.today()
    offset = today.weekday() % 7 + 1
    this_sunday = today - timedelta(days=offset)

    duration_str = _("==========").ljust(21) + "\t"
    for week in range(0, ws+1):
        sunday_begin = this_sunday - timedelta(weeks=week)
        sunday_end = this_sunday - timedelta(weeks=week-1)
        duration_str += format_header(None, None, None, _(sunday_begin) + _("->") + _(sunday_end))
    print(duration_str)

    header_str = _("Author").ljust(21) + "\t"
    for i in range(0, ws+1):
        header_str += format_header(_("Commits"), _("Insertions"), _("Deletions"), _("Net"))
    print(header_str)

    db = shelve.open(DB_FILE)
    for author in db.keys():
        report_line = _(author).ljust(21) + "\t"
        report = db[author]
        for week in range(0, ws+1):
            sunday = this_sunday - timedelta(weeks=week)
            if not report.has_key(str(sunday)):
                report_line += format_header(_("0"), _("0"), _("0"), ("0"))
            else:
                statistic = report[str(sunday)]
                report_line += format_statistic(str(statistic[0]), str(statistic[1]), str(statistic[2]),
                                                str(statistic[1] - statistic[2]))
        print(report_line)
    db.close()


def debug_print(s):
    if DEBUG:
        print(s)