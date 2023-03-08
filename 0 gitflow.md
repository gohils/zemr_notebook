## Initialize

gitflow | git
--------|-----
`git flow init` | `git init`
&nbsp; | `git commit --allow-empty -m "Initial commit"`
&nbsp; | `git checkout -b develop master`


## Connect to the remote repository

gitflow | git
--------|-----
_N/A_ | `git remote add origin git@github.com:MYACCOUNT/MYREPO`


## Features

### Create a feature branch

gitflow | git
--------|-----
`git flow feature start MYFEATURE` | `git checkout -b feature/MYFEATURE develop`


### Share a feature branch

gitflow | git
--------|-----
`git flow feature publish MYFEATURE` | `git checkout feature/MYFEATURE`
&nbsp; | `git push origin feature/MYFEATURE`


### Get latest for a feature branch

gitflow | git
--------|-----
`git flow feature pull origin MYFEATURE` | `git checkout feature/MYFEATURE`
&nbsp; | `git pull --rebase origin feature/MYFEATURE`


### Finalize a feature branch

gitflow | git
--------|-----
`git flow feature finish MYFEATURE` | `git checkout develop`
&nbsp; | `git merge --no-ff feature/MYFEATURE`
&nbsp; | `git branch -d feature/MYFEATURE`


### Push the merged feature branch

gitflow | git
--------|-----
_N/A_ | `git push origin develop`
&nbsp; | `git push origin :feature/MYFEATURE` _(if pushed)_


## Releases

### Create a release branch

gitflow | git
--------|-----
`git flow release start 1.2.0` | `git checkout -b release/1.2.0 develop`


### Share a release branch

gitflow | git
--------|-----
`git flow release publish 1.2.0` | `git checkout release/1.2.0`
&nbsp; | `git push origin release/1.2.0`


### Get latest for a release branch

gitflow | git
--------|-----
_N/A_ | `git checkout release/1.2.0`
&nbsp; | `git pull --rebase origin release/1.2.0`


### Finalize a release branch

gitflow | git
--------|-----
`git flow release finish 1.2.0` | `git checkout master`
&nbsp; | `git merge --no-ff release/1.2.0`
&nbsp; | `git tag -a 1.2.0`
&nbsp; | `git checkout develop`
&nbsp; | `git merge --no-ff release/1.2.0`
&nbsp; | `git branch -d release/1.2.0`


### Push the merged feature branch

gitflow | git
--------|-----
_N/A_ | `git push origin master`
&nbsp; | `git push origin develop`
&nbsp; | `git push origin --tags`
&nbsp; | `git push origin :release/1.2.0` _(if pushed)_


## Hotfixes

### Create a hotfix branch

gitflow | git
--------|-----
`git flow hotfix start 1.2.1 [commit]` | `git checkout -b hotfix/1.2.1 [commit]`


### Finalize a hotfix branch

gitflow | git
--------|-----
`git flow hotfix finish 1.2.1` | `git checkout master`
&nbsp; | `git merge --no-ff hotfix/1.2.1`
&nbsp; | `git tag -a 1.2.1`
&nbsp; | `git checkout develop`
&nbsp; | `git merge --no-ff hotfix/1.2.1`
&nbsp; | `git branch -d hotfix/1.2.1`


### Push the merged hotfix branch

gitflow | git
--------|-----
_N/A_ | `git push origin master`
&nbsp; | `git push origin develop`
&nbsp; | `git push origin --tags`
&nbsp; | `git push origin :hotfix/1.2.1` _(if pushed)_



## References

 - http://nvie.com/posts/a-successful-git-branching-model/


Git Commands
============

_A list of my commonly used Git commands_


### Getting & Creating Projects

| Command | Description |
| ------- | ----------- |
| `git init` | Initialize a local Git repository |
| `git clone ssh://git@github.com/[username]/[repository-name].git` | Create a local copy of a remote repository |

### Basic Snapshotting

| Command | Description |
| ------- | ----------- |
| `git status` | Check status |
| `git add [file-name.txt]` | Add a file to the staging area |
| `git add -A` | Add all new and changed files to the staging area |
| `git commit -m "[commit message]"` | Commit changes |
| `git rm -r [file-name.txt]` | Remove a file (or folder) |

### Branching & Merging

| Command | Description |
| ------- | ----------- |
| `git branch` | List branches (the asterisk denotes the current branch) |
| `git branch -a` | List all branches (local and remote) |
| `git branch [branch name]` | Create a new branch |
| `git branch -d [branch name]` | Delete a branch |
| `git push origin --delete [branch name]` | Delete a remote branch |
| `git checkout -b [branch name]` | Create a new branch and switch to it |
| `git checkout -b [branch name] origin/[branch name]` | Clone a remote branch and switch to it |
| `git branch -m [old branch name] [new branch name]` | Rename a local branch |
| `git checkout [branch name]` | Switch to a branch |
| `git checkout -` | Switch to the branch last checked out |
| `git checkout -- [file-name.txt]` | Discard changes to a file |
| `git merge [branch name]` | Merge a branch into the active branch |
| `git merge [source branch] [target branch]` | Merge a branch into a target branch |
| `git stash` | Stash changes in a dirty working directory |
| `git stash clear` | Remove all stashed entries |

### Sharing & Updating Projects

| Command | Description |
| ------- | ----------- |
| `git push origin [branch name]` | Push a branch to your remote repository |
| `git push -u origin [branch name]` | Push changes to remote repository (and remember the branch) |
| `git push` | Push changes to remote repository (remembered branch) |
| `git push origin --delete [branch name]` | Delete a remote branch |
| `git pull` | Update local repository to the newest commit |
| `git pull origin [branch name]` | Pull changes from remote repository |
| `git remote add origin ssh://git@github.com/[username]/[repository-name].git` | Add a remote repository |
| `git remote set-url origin ssh://git@github.com/[username]/[repository-name].git` | Set a repository's origin branch to SSH |

### Inspection & Comparison

| Command | Description |
| ------- | ----------- |
| `git log` | View changes |
| `git log --summary` | View changes (detailed) |
| `git log --oneline` | View changes (briefly) |
| `git diff [source branch] [target branch]` | Preview changes before merging |


### commands to discard all local changes in Git are:
| Command | Description |
| ------- | ----------- |
|git reset –hard|
|git clean -fxd|

### Create


| Operation                                      | Command                    |
|------------------------------------------------|----------------------------|
| Clone an existing repository  | `$ git clone ssh://user@domain.com/repo.git`|
| Create a new local repository | `$ git init`                                |

### Local Changes

| Operation                                      | Command                    |
|------------------------------------------------|----------------------------|
| Changed files in your working directory | `$ git status` |
| Changes to tracked files | `$ git diff` |
| Add all current changes to the next commit | `$ git add .` |
| Add some changes in <file> to the next commit | `$ git add -p <file>` |
| Commit all local changes in tracked files | `$ git commit -a` |
| Commit previously staged changes | `$ git commit` |
| Change the last commit (__Don‘t amend published commits!__) | `$ git commit --amend` |

### Commit History

| Operation                                      | Command                    |
|------------------------------------------------|----------------------------|
| Show all commits, starting with newest | `$ git log` |
| Show changes over time for a specific file | `$ git log -p <file>` |
| Who changed what and when in <file> | `$ git blame <file>` |

### Branches and Tags

| Operation                                      | Command                    |
|------------------------------------------------|----------------------------|
| List all existing branches | `$ git branch` |
| Switch HEAD branch | `$ git checkout <branch>` |
| Create a new branch based on your current HEAD | `$ git branch <new-branch>` |
| Create a new tracking branch based on a remote branch | `$ git checkout --track <remote/branch>` |
| Delete a local branch | `$ git branch -d <branch>` |
| Mark the current commit with a tag | `$ git tag <tag-name>` |

### Update and Publish

| Operation                                      | Command                    |
|------------------------------------------------|----------------------------|
| List all currently configured remotes | `$ git remote -v` |
| Show information about a remote | `$ git remote show <remote>` |
| Add new remote repository, named <remote> | `$ git remote add <remote> <url>` |
| Download all changes from <remote>, but don‘t integrate into HEAD | `$ git fetch <remote>` |
| Download changes and directly merge/ integrate into HEAD | `$ git pull <remote> <branch>` |
| Publish local changes on a remote | `$ git push <remote> <branch>` |
| Delete a branch on the remote | `$ git branch -dr <remote/branch>` |
| Publish your tags | `$ git push --tags` |

### Merge and Rebase

| Operation                                      | Command                    |
|------------------------------------------------|----------------------------|
| Merge <branch> into your current HEAD | `$ git merge <branch>` |
| Rebase your current HEAD onto <branch> (__Don‘t rebase published commits!__) | `$ git rebase <branch>` |
| Abort a rebase | `$ git rebase --abort` |
| Continue a rebase after resolving conflicts | `$ git rebase --continue` |
| Use your configured merge tool to solve conflicts | `$ git mergetool` |
| Use your editor to manually solve con- flicts and (after resolving) mark file as resolved | `$ git add <resolved-file> $ git rm <resolved-file>` |

### Undo

| Operation                                      | Command                    |
|------------------------------------------------|----------------------------|
| Discard all local changes in your working directory | `$ git reset --hard HEAD` |
| Discard local changes in a specific file | `$ git checkout HEAD <file>` |
| Revert a commit (by producing a new commit with contrary changes) | `$ git revert <commit>` |
| Reset your HEAD pointer to a previous commit and discard all changes since then | `$ git reset --hard <commit>` |
| Reset your HEAD pointer to a previous commit and preserve all changes as unstaged changes | `$ git reset <commit>` |
| Reset your HEAD pointer to a previous commit and preserve uncommitted local changes | `$ git reset --keep <commit>` |
 
 
