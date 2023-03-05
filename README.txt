# create virtual environment

python -m venv .venv
.venv\Scripts\activate

pip install setuptools wheel
pip install -r requirements.txt 
create setup.py
python setup.py sdist bdist_wheel

pip list
The following is need to install library locally to avoid module not found error
pip install -e .

---- download python wheel dependecies from pypi to local dir
pip wheel -r requirements.txt --wheel-dir=./wheelhouse 
---- install python wheel dependecies from local wheels dir
pip install -r requirements.txt --no-index --find-links=./wheelhouse 


Python design patterns - https://sbcode.net/python/
https://aws.amazon.com/blogs/big-data/automate-amazon-redshift-serverless-data-warehouse-management-using-aws-cloudformation-and-the-aws-cli/ </br>
https://aws.amazon.com/blogs/big-data/automate-amazon-redshift-cluster-creation-using-aws-cloudformation/

####  Git Command for new feature branch and merge conflict for pull request from feature to master
####  Introduction 
AWS CICD repo1
####  The overall flow of Gitflow is:

####  1 - A develop branch is created from main
####  2 - A release branch is created from develop
####  3 - Feature branches are created from develop
####  4 - When a feature is complete it is merged into the develop branch
####  5 - When the release branch is done it is merged into develop and main
####  6 - If an issue in main is detected a hotfix branch is created from main
####  7 - Once the hotfix is complete it is merged to both develop and main


####  A complete example demonstrating a Feature Branch Flow is as follows. Assuming we have a repo setup with a main branch.

The commands to discard all local changes in Git are:
git reset –hard
git clean -fxd

git checkout main

git checkout -b develop

git checkout -b feature_branch
####  work happens on feature branch

echo 'feature' >>  test_feature1.txt

git add .
git commit -m "feature1 v1 complete"
push local branch to remore
git push -u origin feature_branch
# create virtual environment

python -m venv .venv
.venv\Scripts\activate

pip install setuptools wheel
pip install -r requirements.txt 
create setup.py
python setup.py sdist bdist_wheel

pip list
The following is need to install library locally to avoid module not found error
pip install -e .

---- download python wheel dependecies from pypi to local dir
pip wheel -r requirements.txt --wheel-dir=./wheelhouse 
---- install python wheel dependecies from local wheels dir
pip install -r requirements.txt --no-index --find-links=./wheelhouse 


git checkout develop
git merge feature_branch
git checkout main
git merge develop
git branch -d feature_branch

git branch

####  In addition to the feature and release flow, a hotfix example is as follows:
git checkout main
git checkout -b hotfix_branch
####  work is done commits are added to the hotfix_branch
echo 'hotfix---v1' >>   hotfix1.txt
git add .
git commit -m "hotfix1 for v1 complete"

git checkout develop
git merge hotfix_branch
git checkout main
git merge hotfix_branch

git checkout develop
git merge feature_branch
git checkout main
git merge develop
git branch -d feature_branch

####  GitFlow
create empty brach locally and push it to remote
git branch develop
git branch
git push -u origin develop
git push --set-upstream origin develop

git checkout develop
git checkout -b feature1_branch
touch test1.txt
git add .
git commit -m "feature1 v1 complete"

push local feature branch to remote repo 
git push -u origin feature1_branch

git checkout develop
git merge feature1_branch

#####  release workflow
git checkout develop
git checkout -b release/0.1.0

git checkout main
git merge release/0.1.0

--------------------------------------------------------------------------------------------


git clone https://github.com/gohils/1Azure.git

cd 1Azure

git add --all or git remote add origin https://github.com/gohils/1Azure.git

git commit -m "new version comments"

git push or git push -u origin master


create a new repository on the command line
echo "####  1Azure" >> README.md

git init

git add README.md

git commit -m "first commit"

git remote add origin https://github.com/gohils/1Azure.git

git push -u origin master

####  create new feature branch
git checkout -b feature1-branch

echo 'feature1_test' >> feature-x-poc_file6.txt

git status

git add .

git commit -m "feature-1-v1"

####  push local feature branch
git push origin feature1-branch:feature1-branch

####  push local changes feature branch
git push --set-upstream origin feature1-branch

git status
git branch 

####  switch to master branch
git checkout master
####  merge feature to master
git merge feature1-branch

####  switch to feature1-branch branch
git checkout feature1-branch

####  resolve merge conflict - get up to date changes into feature from master origin and resolve merge in feature from master
git diff --name-only

git checkout feature1-branch

git fetch origin        
git merge origin/master
git diff --name-only

####  Click "Source Control" button on left. -> See MERGE CHANGES in sidebar. -> Those files have merge conflicts.->select accept current change or incoming change for each file and save and commit again

git add .

git commit -m "merge fix v0.1"

git push

####  complete pull request and delete feature1-branch from local repo
git fetch

git checkout master

git branch -d feature1-branch

#

                



…or push an existing repository from the command line

git remote add origin https://github.com/gohils/1Azure.git

git push -u origin master


mkdir git_ex1 ####  Create a folder called git_ex1 
cd git_ex1 ####  `cd` into the folder git_ex1 
git init ####  Initialize a git repository

echo 'alice' >> file1.txt
git add . && git commit -m "1st git commit: 1 file"

echo 'becky' >> file2.txt
git add . && git commit -m "2nd git commit: 2 files"

echo 'callie' >> file3.txt
git add . && git commit -m "3rd git commit: 3 files"

echo 'diana' >> file4.txt
git add . && git commit -m "4th git commit: 4 files"

echo 'ellen' >> file5.txt
git add . && git commit -m "5th git commit: 5 files"

####  create new feature branch
git checkout -b feature1-branch

echo 'feature1_test' >> feature-x-poc_file6.txt
git status

####  push local feature branch
git push origin feature1-branch:feature1-branch

git add . && git commit -m "feature-x-poc git commit: 6 files"

####  push local changes feature branch
git push --set-upstream origin feature1-branch

git status
git branch 

####  switch to master branch
git checkout master
####  merge feature to master
git merge feature1-branch

####  switch to feature1-branch branch
git checkout feature1-branch

####  resolve merge conflict - get up to date changes into feature from master origin and resolve merge in feature from master
git checkout feature1-branch
git fetch origin        
git merge origin/master

git commit -m "merge fix v0.1"
####  complete pull request


####  delete feature branch after merge
git branch -d feature1-branch

####  tag stable good version last commit-id and tag can be referred instead of commit-id in all git command
git tag -a v1.0 

git log --oneline

####  Start a new feature
git checkout -b new-feature master
####  Edit some files
echo 'Start a new feature' >> feature_file7.txt
git add feature_file7.txt
git commit -m "Start a new feature"
####  Edit some files
echo 'Finish a new feature' >> feature_file7.txt
git add feature_file8.txt
git commit -m "Finish a new feature"
####  Merge in the new-feature branch
git checkout master
git merge new-feature
git branch -d new-feature

####  tag stable good version commit-id
git tag -a v1.1 commit-id

git tag -a v1.2 commit-id

git log --oneline

####  undo uncommited file change

echo 'Start a new feature x changes' >> feature_file_x1.txt
git add feature_file7.txt
git commit -m "Start a new feature x changes"
####  Edit some files
echo 'Finish a new feature x changes' >> feature_file_x1.txt

git restore --staged  feature_file_x1.txt
git restore -- .

####  revert will undo changes for specific commit and create new commit
git revert commit-id

####  reset will delete commit history
git reset commit-id
git reset --hard v1.0

git diff first_commit last_commit

git diff v1.1 v1.2


####  OH NO! We want to undo the commit with the text "WRONG" - let's learn revert!
#####  Create a folder called `learn_revert`
mkdir learn_revert 
####  `cd` into the folder `learn_revert`
cd learn_revert 
git init ####  Initialize a git repository
####  Create a file called `first.txt`
touch first.txt 
####  Add the text "Start" to `first.txt`
echo Start >> first.txt 

####  Add the `first.txt` file
git add . 
####  Commit with the message "Adding first.txt"
git commit -m "adding first" 

####  Add the text "WRONG" to `wrong.txt`
echo WRONG > wrong.txt 
####  Add the `wrong.txt` file
git add . 
####  Commit with the message "Adding WRONG to wrong.txt"
git commit -m "adding WRONG to wrong.txt" 

####  Add the text "More" to `first.txt`
echo More >> first.txt 
####  Add the `first.txt` file
git add . 
####  Commit with the message "Adding More to first.txt"
git commit -m "adding More to first.txt" 

####  Add the text "Even More" to `first.txt`
echo Even More >> first.txt 
####  Add the `first.txt` file
git add . 
####  Commit with the message "Adding More to first.txt"
git commit -m "adding Even More to First.txt" 

######  let's revert! Since this commit was 2 from where we are not we can use git revert HEAD~2 (or we can use git log and find the SHA of that commit)

####  this will put us in a text editor where we can modify the commit message.
git revert HEAD~2 

####  wrong.txt is not there any more!
ls 
####  note that the commit history hasn't been altered, we've just added a new commit reflecting the removal of the `wrong.txt`

git log --oneline 



