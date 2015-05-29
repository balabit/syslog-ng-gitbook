# Getting started to syslog-ng
#### *lightning guide to understand the basics of the project*

Syslog-ng team has started this guide in order to wide the community of
contributors via providing a short and fair description to the project.
This document was written for users and developers. You can find sections
about installing syslog-ng, others are for introducing you to the tools 
and techniques we use.

We hope after reading our GitBook you will find it useful and will be ready
to create your ideas!
Feel free to contribute and propose your chapter ideas!

### GitBook

available here: [syslog-ng-gitbook](https://www.gitbook.com/book/syslog-ng/getting-started/details)

### Syslog-ng project
[![Build Status](https://travis-ci.org/balabit/syslog-ng.svg?branch=master)](https://travis-ci.org/balabit/syslog-ng)
[![Build Status](https://drone.io/github.com/balabit/syslog-ng/status.png)](https://drone.io/github.com/balabit/syslog-ng/latest)

available here: [syslog-ng](https://github.com/balabit/syslog-ng)

### Waffle.io
[![Stories in Ready](https://badge.waffle.io/balabit/syslog-ng-gitbook.svg?label=ready&title=Ready)](http://waffle.io/balabit/syslog-ng-gitbook)

We use waffle.io to track the issues.

### TravisCI

We are planning to use CI with the repository to avoid typos and compile errors.

### Vagrant

You can find a `Vagrantfile` in the repository that you can use to install a development environment to test
your modifications. 

* Install [VirtualBox](https://www.virtualbox.org/wiki/Downloads) for we use it as a provider of the devenv.
Naturally you can use other providers like Docker, VMWare. [Read more](http://docs.vagrantup.com/v2/providers/)
* [Install Vagrant](https://www.vagrantup.com/downloads.html)
* Run the shell commands below in the root directory of the project
```shell
  vagrant box add ubuntu/trusty # downloading the proper image
  vagrant up                    # powering up your vm
  vagrant ssh                   # ssh into the vm
```
* In the VM go to `/home/vagrant/project` and use `gitbook serve` command to start compiling 
the book. You can reach the locally rendered gitbook on `http://localhost:4000`.

### Contribution
* We use branches to isolate the modifications to different chapters. Please send the PR
to the proper branch you made modifications to.
* Please test your modifications using the `Vagrantfile` provided. Later TravisCI will also run
some tests on the repository to avoid problems.


