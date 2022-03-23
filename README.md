# Hoop - Libraries: Hoop

### Deployment

Simply push to master, then Bob will build with tag `YY.MM-X`

* `YY` is the last two digits of the current year
* `MM` is the month
* `X` is an incremental build number for that particular month and year

If you have pushed a branch, Bob will tag that branch by its name, followed by the build version

e.g. for branch `my-great-branch`, with the date being 5th December 2019, Bob will tag it as `my-great-branch-19.12-1`

### Usage in your project

Just make sure you are using the right version in the requirements.txt file
