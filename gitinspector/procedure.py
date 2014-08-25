import subprocess
import interval

HIDE_ERR_OUTPUT = " >/dev/null 2>&1"


def git_cleanup_and_reset():
    output = subprocess.Popen("git clean -fd && git reset HEAD --hard" + HIDE_ERR_OUTPUT,
                              shell=True, bufsize=1, stdout=subprocess.PIPE).stdout
    output.readlines()


def create_branches_for_inspection():
    print("Cleaning current branch ...")
    git_cleanup_and_reset()

    print("Fetch all branches ...")
    output = subprocess.Popen("git fetch --all" + HIDE_ERR_OUTPUT, shell=True, bufsize=1, stdout=subprocess.PIPE).stdout
    output.readlines()

    print("Creating branches for inspection ...")
    output = \
        subprocess.Popen("for remote in `git branch -r `; do " +
                         "   if [[ $remote != *HEAD* && $remote == origin* ]]; then " +
                         "      git checkout -b ${remote/origin\//insp\/} $remote; " +
                         "   fi; " +
                         "done" + HIDE_ERR_OUTPUT, shell=True, bufsize=1, stdout=subprocess.PIPE).stdout
    output.readlines()


def remove_inspection_branches():
    print("Removing all branches for inspection ...")
    output = subprocess.Popen("for remote in `git branch -r `; do git branch -D ${remote/origin\//insp\/}; done"
                              + HIDE_ERR_OUTPUT,
                                          shell=True, bufsize=1, stdout=subprocess.PIPE).stdout
    output.readlines()

def get_last_commit_date(commit):
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
        since_date_time = "2014-08-24"
    return get_last_commit_date(commit) > '2014-08-24'

def switch_to_branch(branch_name):
    git_cleanup_and_reset()

    print("\n============ Inspecting " + branch_name)
    output = \
        subprocess.Popen("git checkout -f " + branch_name + HIDE_ERR_OUTPUT,
                         shell=True, bufsize=1, stdout=subprocess.PIPE).stdout
    lines = output.readlines()
    return True