# General Failure Recovery/Remote Access Plan

This document outlines the steps needed in order to access a codebase on a completely different computer, to make changes, fix bugs, and recover from failure. This document assumes that I am running the application on Heroku, and describes a method based on a Python environment.

## Requirements

This plan is tailored for applications that meet the following characteristics:

+ A Heroku staging/production environment
+ Python-based application
+ The project must have a private remote on BitBucket.
+ Depending on the application requirements, it may include other services such as a backend or caching system.

## Steps

Assuming I have access to a "random" (what really is random?) computer, these are the steps I would take to be able to safely access the codebase, make changes, upload the changes to the live server, and return those changes back to my local environment.

1. Download and install Git.
2. Open [Bitbucket](https://bitbucket.com) and login to my account.
3. Create a git clone of the appropriate bitbucket private project repository (will be prompted for credentials). Note that this will create a git remote for this local repository pointing to the Bitbucket server repository named `origin`.

  ```bash
  git clone https://username@bitbucket.org/username/repository.git
  ```

4. With local checkout created, set the git **local** configuration user email to the same one associated with the Bitbucket account. Changing the local configuration and not the global configuration makes it easier to remove credentials later.

  ```bash
  git config --local user.email "myemail@email.com"

  # check to see if credentials properly set
  got config --local -l
  ```

5. Download and install Python (ensure that I download the correct version).
6. Install pip.
7. Install virtualenv.
8. Turn the cloned repository into a virtual environment and activate it.

  ```bash
  # create virtual environment
  virtualenv repository

  # activate
  cd repository
  source bin/activate
  ```

9. Install repository requirements with pip.

  ```bash
  pip install -r requirements.txt
  ```

10. Open [Heroku](https://heroku.com) and login to my account.
11. Download and install the Heroku CLI.
12. Login to Heroku on the CLI.

  ```bash
  heroku login
  ```

13. Set the Heroku application as a remote for this local repository.

  ```bash
  git remote heroku https://git.heroku.com/application.git

  # check to see if remote was properly set
  git remote -v
  ```

14. Make necessary changes to local repository (test out locally if possible).
15. Stage and commit changes.

  ```bash
  git add -A
  git commit -m "message here"
  ```

16. Push changes to Bitbucket (will be prompted for credentials).

  ```bash
  git push origin master
  ```

17. Push changes to Heroku.

  ```bash
  git push heroku master
  ```

18. Clear Heroku credentials from computer.

  ```bash
  heroku logout
  ```

19. Remove email from git config. Note for more security, inspect the global configuration file (where is that found?) and the repository local configuration file at `.git/config`.

  ```bash
  git config --local --unset-all user.email

  # check to make sure that the operation was successful
  git config --global -l
  git config --local -l
  ```

20. Pull the changes from Bitbucket to my local computer.

  ```bash
  git pull bitbucket master
  ```

**Note**: The use of Bitbucket here is extraneous, as the whole repository is still available from the Heroku application. In fact, we can clone the application from Heroku using:

```bash
heroku git:clone -a application
```

The Bitbucket association gives a safer way to share this code with others, separate from the live application, and at this point is just a personal preference. The drawbacks of maintaining this process is that I have to coordinate between 2 remotes, and make sure I push/pull properly.
