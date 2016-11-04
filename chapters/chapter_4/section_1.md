# tools

## GitHub
GitHub is a code sharing and publishing service. It provides git repositories
with many different services that can be integrated into your development process.
Open-source projects can be communicated on GitHub for it has a great issue and collaboration system.
We also use GitHub issues to discuss feature requests and track the process of development via
syncing our ideas successively.

We also prefer contributing via forking our repository and sending pull-requests from your forked repo
to ours on GitHub.

[Sign up on GitHub](http://github.com/join)

[Balabit repositories](http://github.com/balabit)

[Balabit/Syslog-ng repository](http://github.com/balabit/syslog-ng)

[Balabit/Syslog-ng issues](http://github.com/balabit/syslog-ng/issues)

## Waffle.io
[Waffle.io](http://waffle.io) is a kanban styled issue management tool that helps you classify your backlogs state during
the process of development. It supports integration to GitHub so issues on GitHub are totally alike backlogs
on Waffle.io. This new perspective given by this tool offers you the opportunity to see the pipeline of
development. You can register using your GitHub account.

We would like to give you an overview about columns in our Waffle.io.

[Balabit’s Waffle.io table](http://waffle.io/balabit/syslog-ng)

#### Feature proposals
Feature proposals are a newly created column in our table. We would like to expand the capabilities of
syslog-ng so we decided to create this place for ideas. We would like to give you a template for these kind 
of proposals that is only an offer and help for you to follow. Using this guide you can create a proper 
description of your idea that is easy to catch.

1. **Short description:**
Description of your feature in 3-5 sentences. Try to focus on functionality, high-level use-case.

2. **Use-case:**
Description of the reasons why you think it is a good idea to implement this feature into syslog-ng.

3. **Done definition:**
Short description when you think this feature is implemented. It is advised that you associate to
use-cases mentioned above.

4. **Realization:**
Description of the process of implementation you think that is advised to follow. 

5. **Questions:**
List of questions, you think, should be discussed before implementation.

#### Backlog
An item in this column represents a task connected to bugs, smaller feature proposals to already existing
features. Issues created the first time are placed here.

#### Blocked
A task in this columns shows that it is stuck for some reason or community do not want to deal with it. 

#### Ready
An item from backlog is moved here if details are known how it should be solved.

#### In progess
In progress column show the issues someone is currently working on. GitHub issues automatically get a tag
`in progress` when they are moved here.

#### Done
An issue is done when it’s done definition is fulfilled or community consider it to be done.

## Travis CI [![Build Status](https://travis-ci.org/balabit/syslog-ng.svg?branch=master)](https://travis-ci.org/balabit/syslog-ng)

Travis CI is a continuous integration service that is free for open-source projects. You can specify 
the process of deploying your product in .travis.yml file that runs every-each time when you push your branch
to the repository.

Our Travis CI runs tests and checks on Linux and MacOSX platform using gcc and clang compilers to test the build.
It is advised to integrate Travis CI with your forked repository to test every-each commits you push. If you wouldn’t
like to do this CI will be run on your pull-request.

[Travis CI](http://travis-ci.org)

[Travis CI balabit/syslog-ng](http://travis-ci.org/balabit/syslog-ng)

## Criterion

Criterion is a unit test framework used in the unit tests of syslog-ng. It can be compiled from 
source or installed as it is available as a .deb package.

Its documentation is extensive and full of examples. More test examples can be found in the source of 
syslog-ng under the `tests/unit` folder.

### Installation on Ubuntu

```
$ curl http://download.opensuse.org/repositories/home:/laszlo_budai:/syslog-ng/xUbuntu_12.04/Release.key | sudo apt-key add -
$ echo "deb http://download.opensuse.org/repositories/home:/laszlo_budai:/syslog-ng/xUbuntu_12.04 ./" | sudo tee --append /etc/apt/sources.list.d/syslog-ng-obs.list
$ sudo apt install criterion criterion-dev
```

[Documentation of Criterion](https://criterion.readthedocs.io/en/master/)

## Astyle

Astyle is a source code formatter which makes sure that all of the C sources are formatted properly. 
Please make sure that version `2.05.1` is installed, as there might be differences between the formatting 
of different versions.

The version `2.05.1` can be also installed from the OBS repository used above.

### Usage

It is advised to format sources before submitting a PR. This makes easier to process PRs both for the reviewers and the contributors. To check if there is a adly formatted file run `make style-check`. To correct 
badly formatted ones run `make style-format`.

Following is the sampla output of calling these commands.

```
$ make style-check
Checking C source files
Formatting tests/unit/test_example.c
Number of badly formatted files: 1
$ make style-format
Formatting C source files
Formatting tests/unit/test_example.c
```

## Coverity

Coverity is an online service that helps you to analyze your code statically (Coverity Scan). It can reveal many defects
that is hidden in your code. It also categorize your defects on many different aspects like priority, security risk,
kind and calculates defect density that can be compared to other open-source projects. 
Coverity Scan can be integrated to Travis CI if needed in order to run the analyzation on code automatically.

You can also have Coverity Scan on your fork but we don’t advise it for it takes a long time to configure and this 
analyzis can be run only limited times a week for open-source projects. We will run analyzis before every releases to
solve defects.

[Coverity website](http://coverity.com)

[Scan Coverity website ](http://scan.coverity.com)
