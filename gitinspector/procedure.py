import subprocess


def create_branches_for_inspection():
    print("Cleaning current branch ...")
    clean_current_branch = subprocess.Popen("git clean -fd && git reset HEAD --hard",
                                            shell=True, bufsize=1, stdout=subprocess.PIPE).stdout

    print("Fetch all branches ...")
    fetch_all_branches = subprocess.Popen("git fetch --all", shell=True, bufsize=1, stdout=subprocess.PIPE).stdout

    print("Creating branches for inspection ...")
    create_branches_for_inspection = \
        subprocess.Popen("for remote in `git branch -r `; do " +
                         "   if [[ $remote != *HEAD* && $remote == origin* ]]; then " +
                         "      git checkout -b ${remote/origin\//insp\/} $remote; " +
                         "   fi; " +
                         "done", shell=True, bufsize=1, stdout=subprocess.PIPE).stdout


def remove_inspection_branches():
    print("Removing all branches for inspection ...")
    subprocess.Popen("for remote in `git branch -r `; do git branch -D ${remote/origin\//insp\/}; done >/dev/null 2>&1",
                                          shell=True, bufsize=1, stdout=subprocess.PIPE)