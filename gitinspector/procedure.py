import os
import subprocess
import interval
from datetime import datetime
from datetime import timedelta

HIDE_ERR_OUTPUT = " >/dev/null 2>&1"
COMMIT_LIST_FILE = ".gi_commit"


def git_cleanup_and_reset():
    output = subprocess.Popen("git clean -fd && git reset HEAD --hard" + HIDE_ERR_OUTPUT,
                              shell=True, bufsize=1, stdout=subprocess.PIPE).stdout
    output.readlines()


def create_branches_for_inspection():
    print("Cleaning current branch ...")
    git_cleanup_and_reset()

    print("Fetch all branches ...")
    err_output = subprocess.Popen("git fetch --all", shell=True, bufsize=1, stdout=subprocess.PIPE).stdout
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


def remove_inspection_branches():
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


def get_processed_commits():
    if os.path.isfile(COMMIT_LIST_FILE) and len(__processed_commits__) == 0:
        processed_commits = []
        with open(COMMIT_LIST_FILE, "rb") as f:
            processed_commits.extend(f.readlines())

    return __processed_commits__


def append_process_commit(commit):
    __processed_commits__.append(commit)
    with open(COMMIT_LIST_FILE, "a") as f:
        f.write(commit + "\n")