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

----------------------------------------------------------------------------------------
Data Quality Dimension
Data Accuracy => e.g. check if country name, state name is valid from the list of value 
Data Validity => e.g. check if format, type if telephone is number, email,date format etc 
Data Timeliness => timely avaliability of data - weekly,daily,hourly 
Data Completeness => check if field name/phone number/email is populated, null check control file to indicate the transmission is successful, check number of records
Data Uniqueness => check if duplicate records/primary key validation etc
Data Consistency => data validation across dataset 

----------------------------------------------------------------------------------------
Data Governance Framework is collection of principal,policy and procedure to ensure the quality, integrity, discoverability, observability, security, accessibility, usability and auditability of your data assets.

1) Data quality – data is in correct and consistent form 
2) Data integrity – data is not tampered with as it moves throughout the organization. 
3) Data discoverability - data is easilty discoverable with data catelog. 
4) Data observability – system wide visibility into data movement - data lineage  
5) Data security – data is classified and protected based on its sensitivity 
6) Data accessibility – relevant employees can access the data 
7) Data usability – data is readily available and usable with your tools. 
8) Data auditability – data can be audited to detect problems.

key capabilities for Data Governance Framework
1.	Data Cataloging and Discovery – The automatic identification and physical record of data assets in a unified manner to enable logical search, description, and discovery of an organization’s data. 
2.	Data Classification – Tagging data with appropriate information, privacy, or other sensitivity classifications to secure onward use and protection. 
3.	Data Ownership – Ensuring data is owned for protection, description, access, and quality by accountable and empowered agents within the organization. 
4.	Data Security – Ensuring data is encrypted, obfuscated, tokenized, or has other appropriate security measures applied in line with its classification. Includes capturing evidence of security application and management of data loss prevention. 
5.	Data Sovereignty and Cross-Border Data Sharing – Ensuring data is being stored, accessed, and processed according to jurisdictional rules and prohibitions. 
6.	Data Quality – Ensuring data is fit for purpose according to the core measures of data quality— accuracy, completeness, consistency, validity, relevance, and timeliness.
7.	Data Lifecycle Management – Ensuring data is sourced, stored, processed, accessed, and disposed of in line with its legal, regulatory, and privacy lifecycle requirements, which are often defined in a retention schedule. 
8.	Data Entitlements and Access Tracking – Data must only be accessible to those that are intending to access it. Auditing this access is an important part of evidencing and ensuring control.
9.	Data Lineage – Ensuring it is possible to identify where data has originated, the steps it has undertaken, and where it is being used at a granularity and frequency that is relevant. 
10.	Data Privacy – Define a framework for the protection of the privacy of data subjects that reflects the regulatory and privacy laws governing your organization. Ensure processes and technology are employed to ensure the privacy framework is actively applied. 
11.	Trusted Source Management and Data Contracts – Large organizations may have similar data originating from or processed through a number of sources. Identifying and managing trusted sources and defining consumption data contracts is important to ensure data is being sourced from an agreed source of truth and the overall data architecture is being managed effectively. 
12.	Ethical Use and Purpose – Increasingly, the ethical use of data is being questioned beyond privacy laws and data subject rights. As the use of AI and machine learning increases, it is important to ensure data is being processed in a way that customers would expect according to your company’s code of ethics. 
13.	Master Data Management – Master data is the most commonly used and duplicated data within an organization. It is often the data that describes the core operational aspects of a company (for example, product, customer, employees, and company structure). Ensuring there is a single consistent view of this data is fundamental to accurate and reliable data usage.

----------------------------
Cloud data platform 
Single data platform to store and analyse structure, semi-structure and unstructured data. 
Single data platform that can support batch, real time and machine learning advanced analytical use cases, scale elastically and cost effectively. 

Single data platform to support entire organisation to make fact based informed decision, more often instead of relying on guess work or assumptions. 

Business benefits of using Cloud services –

1.	Agility – With click of button, we can provision service or infrastructure to support new business initiative. We can quickly develop proof of concept to validate feasibility of new business requirements. If proof of concept is successful, Cloud services can accelerate Time-to-market by using infrastructure as a code to quickly deploy required infrastructure and Azure devops platform to quickly build, test and deploy solution. 

2.	scalability – cloud services can be scaled elastically based on business needs – for example scaling up during special promotion or any specific time of the day and scale down to normal at other time

3.	cost effectiveness – business can save cost with the consumption based pricing model and by using latest technological innovation like decoupling of storage from compute, Kubernetes and serverless architecture

4.	Reliability - data backup, disaster recovery and redundancy - automatic failed over etc
5.	Productivity - software upgrade and updating patches. 

6.	Security – Azure provides enterprise grade security with five layer of defence - 
Data protection, Access control, Authentication, Network security, Auditing & advanced threat protection.

--------------------------------------------------------
security with five layer of defence
1 – Data protection which includes data encryption at rest and data encryption in transit , column level encryption, data masking
2 – Access control – which includes fine grain access control with file, folder level access, sql permission for column and level access control 
3 – Authentication – which includes active directory integration with multi-factor authentication.
4 – Network protection which include network isolation with vnet, network security group, firewall protection
5 – auditing, logging, monitoring and alerting with Azure Monitoring and advance threat protection with  Security centre



