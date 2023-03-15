
### commands to discard all local changes in Git are:
| Command | Description |
| ------- | ----------- |
| git log --all --oneline --graph| View changes (briefly) |
| `git diff [source branch] [target branch]` | Preview changes before merging |
| `git diff --name-only` | Preview changes before merging |
|git merge --abort| abort merge conflict |
|git reset –hard| reset local branch to current HEAD |
|git clean -fxd| remove local file which are not part of previous commit |
|git checkout commit_id -- filename.txt | checkout restore file from any commit |

#####  How do I find and restore a deleted file in a Git repository?
git checkout commit_id -- filename.txt -> checkout restore file from any commit
Find the last commit that affected the given path. As the file isn't in the HEAD commit, that previous commit must have deleted it.

git rev-list -n 1 HEAD -- <file_path>
Then checkout the version at the commit before, using the caret (^) symbol:

git checkout <deleting_commit>^ -- <file_path>
Or in one command, if $file is the file in question.

git checkout $(git rev-list -n 1 HEAD -- "$file")^ -- "$file"
If you are using zsh and have the EXTENDED_GLOB option enabled, the caret symbol won't work. You can use ~1 instead.

git checkout $(git rev-list -n 1 HEAD -- "$file")~1 -- "$file"


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
 
 

## Why git?

Git really changed the way developers think of merging and branching. From the classic CVS/Subversion world, merging/branching has always been considered a bit scary and something you only do every once in a while.
But with Git, these actions are extremely cheap and simple, and they are considered one of the core parts of your daily workflow, really.
As a consequence of its simplicity and repetitive nature, branching and merging are no longer something to be afraid of. Version control tools are supposed to assist in branching/merging more than anything else.

## Decentralized but centralized

The repository setup that we use and that works well with this branching model, is that with a central “truth” repo. Note that this repo is only considered to be the central one (since Git is a DVCS, there is no such thing as a central repo at a technical level). We will refer to this repo as origin, since this name is familiar to all Git users.

Each developer pulls and pushes to origin. But besides the centralized push-pull relationships, each developer may also pull changes from other peers to form sub teams. For example, this might be useful to work together with two or more developers on a big new feature, before pushing the work in progress to origin prematurely. In the figure above, there are sub teams of Alice and Bob, Alice and David, and Clair and David.
Technically, this means nothing more than that Alice has defined a Git remote, named bob, pointing to Bob’s repository, and vice versa.


## The main branches 

At the core, the development model is greatly inspired by existing models out there. The central repo holds two main branches with an infinite lifetime:

•	master

•	develop

The master branch at origin should be familiar to every Git user. Parallel to the master branch, another branch exists called develop.
We consider origin/master to be the main branch where the source code of HEAD always reflects a production-ready state.
We consider origin/develop to be the main branch where the source code of HEAD always reflects a state with the latest delivered development changes for the next release. Some would call this the “integration branch”. This is where any automatic nightly builds are built from.
When the source code in the develop branch reaches a stable point and is ready to be released, all of the changes should be merged back into master somehow and then tagged with a release number. How this is done in detail will be discussed further on.
Therefore, each time when changes are merged back into master, this is a new production release by definition. We tend to be very strict at this, so that theoretically, we could use a Git hook script to automatically build and roll-out our software to our production servers every time there was a commit on master.

## Supporting branches 


Next to the main branches master and develop, our development model uses a variety of supporting branches to aid parallel development between team members, ease tracking of features, prepare for production releases and to assist in quickly fixing live production problems. Unlike the main branches, these branches always have a limited life time, since they will be removed eventually.
The different types of branches we may use are:

•	Feature branches

•	Release branches

•	Hotfix branches

Each of these branches have a specific purpose and are bound to strict rules as to which branches may be their originating branch and which branches must be their merge targets. We will walk through them in a minute.
By no means are these branches “special” from a technical perspective. The branch types are categorized by how we use them. They are of course plain old Git branches.

## Feature branches 


May branch off from:

develop

Must merge back into:

develop

Branch naming convention:

anything except master, develop, release-*, or hotfix-*

Feature branches (or sometimes called topic branches) are used to develop new features for the upcoming or a distant future release. When starting development of a feature, the target release in which this feature will be incorporated may well be unknown at that point. The essence of a feature branch is that it exists as long as the feature is in development, but will eventually be merged back into develop (to definitely add the new feature to the upcoming release) or discarded (in case of a disappointing experiment).

Feature branches typically exist in developer repos only, not in origin.

### Creating a feature branch 

When starting work on a new feature, branch off from the develop branch.

			$ git checkout -b myfeature develop
      
			Switched to a new branch "myfeature"


Incorporating a finished feature on develop 

Finished features may be merged into the develop branch to definitely add them to the upcoming release:

$ git checkout develop

Switched to branch 'develop'

$ git merge --no-ff myfeature

Updating ea1b82a..05e9557

(Summary of changes)

$ git branch -d myfeature

Deleted branch myfeature (was 05e9557).

$ git push origin develop

The --no-ff flag causes the merge to always create a new commit object, even if the merge could be performed with a fast-forward. This avoids losing information about the historical existence of a feature branch and groups together all commits that together added the feature. 


### Compare:
 
In the latter case, it is impossible to see from the Git history which of the commit objects together have implemented a feature—you would have to manually read all the log messages. Reverting a whole feature (i.e. a group of commits), is a true headache in the latter situation, whereas it is easily done if the --no-ff flag was used.
Yes, it will create a few more (empty) commit objects, but the gain is much bigger than the cost.


## Release branches 


May branch off from:

develop

Must merge back into:

develop and master

Branch naming convention:

release-*

Release branches support preparation of a new production release. They allow for last-minute dotting of i’s and crossing t’s. Furthermore, they allow for minor bug fixes and preparing meta-data for a release (version number, build dates, etc.). By doing all of this work on a release branch, the develop branch is cleared to receive features for the next big release.
The key moment to branch off a new release branch from develop is when develop (almost) reflects the desired state of the new release. At least all features that are targeted for the release-to-be-built must be merged in to develop at this point in time. All features targeted at future releases may not—they must wait until after the release branch is branched off.
It is exactly at the start of a release branch that the upcoming release gets assigned a version number—not any earlier. Up until that moment, the develop branch reflected changes for the “next release”, but it is unclear whether that “next release” will eventually become 0.3 or 1.0, until the release branch is started. That decision is made on the start of the release branch and is carried out by the project’s rules on version number bumping.



### Creating a release branch 


Release branches are created from the develop branch. For example, say version 1.1.5 is the current production release and we have a big release coming up. The state of develop is ready for the “next release” and we have decided that this will become version 1.2 (rather than 1.1.6 or 2.0). So we branch off and give the release branch a name reflecting the new version number:

$ git checkout -b release-1.2 develop

Switched to a new branch "release-1.2"

$ ./bump-version.sh 1.2

Files modified successfully, version bumped to 1.2.

$ git commit -a -m "Bumped version number to 1.2"

[release-1.2 74d9424] Bumped version number to 1.2

1 files changed, 1 insertions(+), 1 deletions(-)

After creating a new branch and switching to it, we bump the version number. Here, bump-version.sh is a fictional shell script that changes some files in the working copy to reflect the new version. (This can of course be a manual change—the point being that some files change.) Then, the bumped version number is committed.
This new branch may exist there for a while, until the release may be rolled out definitely. During that time, bug fixes may be applied in this branch (rather than on the develop branch). Adding large new features here is strictly prohibited. They must be merged into develop, and therefore, wait for the next big release.

### Finishing a release branch 


When the state of the release branch is ready to become a real release, some actions need to be carried out. First, the release branch is merged into master (since every commit on master is a new release by definition, remember). Next, that commit on master must be tagged for easy future reference to this historical version. Finally, the changes made on the release branch need to be merged back into develop, so that future releases also contain these bug fixes.

The first two steps in Git:

$ git checkout master

Switched to branch 'master'

$ git merge --no-ff release-1.2

Merge made by recursive.

(Summary of changes)

$ git tag -a 1.2

The release is now done, and tagged for future reference.

Edit: You might as well want to use the -s or -u <key> flags to sign your tag cryptographically.
To keep the changes made in the release branch, we need to merge those back into develop, though. In Git:

$ git checkout develop

Switched to branch 'develop'

$ git merge --no-ff release-1.2

Merge made by recursive.

(Summary of changes)

This step may well lead to a merge conflict (probably even, since we have changed the version number). If so, fix it and commit.
Now we are really done and the release branch may be removed, since we don’t need it anymore:

$ git branch -d release-1.2

Deleted branch release-1.2 (was ff452fe).


## Hotfix branches



May branch off from:

master

Must merge back into:

develop and master

Branch naming convention:

hotfix-*

Hotfix branches are very much like release branches in that they are also meant to prepare for a new production release, albeit unplanned. They arise from the necessity to act immediately upon an undesired state of a live production version. When a critical bug in a production version must be resolved immediately, a hotfix branch may be branched off from the corresponding tag on the master branch that marks the production version.
The essence is that work of team members (on the develop branch) can continue, while another person is preparing a quick production fix.


### Creating the hotfix branch 


Hotfix branches are created from the master branch. For example, say version 1.2 is the current production release running live and causing troubles due to a severe bug. But changes on developare yet unstable. We may then branch off a hotfix branch and start fixing the problem:

$ git checkout -b hotfix-1.2.1 master

Switched to a new branch "hotfix-1.2.1"

$ ./bump-version.sh 1.2.1

Files modified successfully, version bumped to 1.2.1.

$ git commit -a -m "Bumped version number to 1.2.1"

[hotfix-1.2.1 41e61bb] Bumped version number to 1.2.1

1 files changed, 1 insertions(+), 1 deletions(-)

Don’t forget to bump the version number after branching off!

Then, fix the bug and commit the fix in one or more separate commits.

$ git commit -m "Fixed severe production problem"

[hotfix-1.2.1 abbe5d6] Fixed severe production problem

5 files changed, 32 insertions(+), 17 deletions(-)


### Finishing a hotfix branch


When finished, the bugfix needs to be merged back into master, but also needs to be merged back into develop, in order to safeguard that the bugfix is included in the next release as well. This is completely similar to how release branches are finished.
First, update master and tag the release.

$ git checkout master

Switched to branch 'master'

$ git merge --no-ff hotfix-1.2.1

Merge made by recursive.

(Summary of changes)

$ git tag -a 1.2.1

Edit: You might as well want to use the -s or -u <key> flags to sign your tag cryptographically.

Next, include the bugfix in develop, too:

$ git checkout develop

Switched to branch 'develop'

$ git merge --no-ff hotfix-1.2.1

Merge made by recursive.

(Summary of changes)

The one exception to the rule here is that, when a release branch currently exists, the hotfix changes need to be merged into that release branch, instead of develop. Back-merging the bugfix into the release branch will eventually result in the bugfix being merged into develop too, when the release branch is finished. (If work in develop immediately requires this bugfix and cannot wait for the release branch to be finished, you may safely merge the bugfix into develop now already as well.)
Finally, remove the temporary branch:

$ git branch -d hotfix-1.2.1

Deleted branch hotfix-1.2.1 (was abbe5d6).

## The branching strategy:


•	feature: All features / new functions / major refactoring is done in feature branches, which branch of and are merged back from/into the develop branch (usually after some kind of peer review).

•	release: When enough features have accumulated or the next release time frame comes near, a new release branch is branched off from develop, which is solely dedicated to testing/bug fixing and any cleanup necessary (e.g. changing some path names, different default values for instrumentation etc.).

•	master Once the QA is satisfied with the quality, the release branch is merged into master (and also back to develop). This is then what is shipped/used by the customers.

•	hotfix If a major problem is found after release, it's fix is developed in a hotfix branch, that is branched of from master. Those are the only branches that will ever branch of master.


•	Note: Any commit in master is a merge commit (either from a release or a hotfix branch) and represents a new release that is shipped to the customer.

	

## How do I find and restore a deleted file in a Git repository?

#####  git checkout commit_id -- filename.txt -> checkout restore file from any commit
Find the last commit that affected the given path. As the file isn't in the HEAD commit, that previous commit must have deleted it.

git rev-list -n 1 HEAD -- <file_path>
Then checkout the version at the commit before, using the caret (^) symbol:

git checkout <deleting_commit>^ -- <file_path>
Or in one command, if $file is the file in question.

git checkout $(git rev-list -n 1 HEAD -- "$file")^ -- "$file"
If you are using zsh and have the EXTENDED_GLOB option enabled, the caret symbol won't work. You can use ~1 instead.

git checkout $(git rev-list -n 1 HEAD -- "$file")~1 -- "$file"
