import subprocess


def create_branches_for_inspection():
    print("Cleaning current branch ...")
    output = subprocess.Popen("git clean -fd && git reset HEAD --hard",
                                            shell=True, bufsize=1, stdout=subprocess.PIPE).stdout
    output.readlines()

    print("Fetch all branches ...")
    output = subprocess.Popen("git fetch --all", shell=True, bufsize=1, stdout=subprocess.PIPE).stdout
    output.readlines()

    print("Creating branches for inspection ...")
    output = \
        subprocess.Popen("for remote in `git branch -r `; do " +
                         "   if [[ $remote != *HEAD* && $remote == origin* ]]; then " +
                         "      git checkout -b ${remote/origin\//insp\/} $remote; " +
                         "   fi; " +
                         "done", shell=True, bufsize=1, stdout=subprocess.PIPE).stdout
    output.readlines()


def remove_inspection_branches():
    print("Removing all branches for inspection ...")
    output = subprocess.Popen("for remote in `git branch -r `; do git branch -D ${remote/origin\//insp\/}; done >/dev/null 2>&1",
                                          shell=True, bufsize=1, stdout=subprocess.PIPE).stdout
    output.readlines()

def get_last_commit_date():
    print("Getting last commit date")
    # git log -1 -s --format="%ci" 3b11c7e004c2dbace43aafa3df73267d63cede09 | cat

def sort_branches_by_last_update():
    print("Sorting branches by last update time")
    # git for-each-ref --sort=-committerdate refs/heads/|grep 'insp'