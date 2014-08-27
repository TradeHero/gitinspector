import os
import subprocess
import threading
import interval
from datetime import datetime
from datetime import timedelta
from os.path import expanduser

HIDE_ERR_OUTPUT = " >/dev/null 2>&1"
COMMIT_LIST_FILE = expanduser("~/.gi_commit")


def git_cleanup_and_reset():
    output = subprocess.Popen("git clean -fd && git reset HEAD --hard" + HIDE_ERR_OUTPUT,
                              shell=True, bufsize=1, stdout=subprocess.PIPE).stdout
    output.readlines()


def create_branches_for_inspection():
    print("Cleaning current branch ...")
    git_cleanup_and_reset()

    switch_to_master_branch()

    print("Fetch all branches ...")
    err_output = subprocess.Popen("git fetch --all --prune", shell=True, bufsize=1, stdout=subprocess.PIPE).stdout
    err_output.readlines()

    print("Creating branches for inspection ...")
    process = \
        subprocess.Popen("for remote in `git branch -r `; do " +
                         "   if [[ $remote != *HEAD* && $remote == origin* ]]; then " +
                         "      git checkout -b ${remote/origin\//insp\/} $remote; " +
                         "   fi; " +
                         "done", shell=True, bufsize=1, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    process_stderr = process.stderr
    err_output = process_stderr.read()
    if ".lock" in err_output:
        print("\n\nPlease ensure that there is not another git process is running on the same repo!")
        print("Delete .git/index.lock file in the current folder and rerun the application again.")
        exit()


def switch_to_master_branch():
    print("Switch back to master branch ...")
    output = subprocess.Popen("git checkout master" + HIDE_ERR_OUTPUT,
                              shell=True, bufsize=1, stdout=subprocess.PIPE).stdout
    output.readlines()


def remove_inspection_branches():
    switch_to_master_branch()

    print("Removing all branches for inspection ...")
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
    print("Sorting branches by last update time ...")
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
    since_date_time = interval.get_since()
    if since_date_time:
        since_date_time = since_date_time.split("=")
        since_date_time = since_date_time[1]
        since_date_time = since_date_time.replace("\"", "")
    else:
        since_date_time = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    return get_commit_date(commit) > since_date_time


def switch_to_branch(branch_name):
    git_cleanup_and_reset()

    print("\n============ Inspecting " + branch_name)
    output = \
        subprocess.Popen("git checkout -f " + branch_name + HIDE_ERR_OUTPUT,
                         shell=True, bufsize=1, stdout=subprocess.PIPE).stdout
    lines = output.readlines()
    return True


def remove_commit_log():
    if os.path.isfile(COMMIT_LIST_FILE):
        os.remove(COMMIT_LIST_FILE)


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
    print("{0}\t\t\t{1}\t\t{2}\t\t{3}".format("Author", "Commits", "Insertions", "Deletions"))
    for author, report in __report__.iteritems():
        print("{0}\t\t\t\t{1}\t\t{2}\t\t{3}".format(author, report.commits, report.insertions, report.deletions))