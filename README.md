# Getting started with syslog-ng

#### _Lightning guide to understand the basics of the project_

The syslog-ng team has started this guide to widen the community of  
contributors by providing a short and fair description to the project.  
This document was written for users and developers. You can find sections  
about installing syslog-ng, others are for introducing you to the tools   
and techniques we use.

We hope that you will find our GitBook useful and will be ready  
to create your own ideas.  
Feel free to contribute and propose your chapter ideas.

### The syslog-ng project

[![Build Status](https://github.com/syslog-ng/syslog-ng/actions/workflows/devshell.yml/badge.svg)](https://ci.syslog-ng.com/view/OSE-DAILY-MONITOR/)

available here: [syslog-ng](https://github.com/balabit/syslog-ng)

### GitBook

available here: [syslog-ng-gitbook](https://syslog-ng.gitbooks.io/getting-started/content/)

### Issue tracker

We use github to [track the issues](https://github.com/balabit/syslog-ng-gitbook/issues).

### TravisCI

We are planning to use CI with the repository to avoid typos and compile errors.

### Vagrant

You can find a `Vagrantfile` in the repository that you can use to install a development environment to test your modifications.

* Install [VirtualBox](https://www.virtualbox.org/wiki/Downloads) for we use it as a provider of the devenv.
  Naturally you can use other providers like Docker, VMware. [Read more](http://docs.vagrantup.com/v2/providers/)
* [Install Vagrant](https://www.vagrantup.com/downloads.html)
* Run the shell commands below in the root directory of the project
  ```shell
  vagrant box add ubuntu/trusty # downloading the proper image
  vagrant up                    # powering up your vm
  vagrant ssh                   # ssh into the vm
  ```
* In the VM go to `/home/vagrant/project` and use the `gitbook serve` command to start compiling 
  the book. You can reach the locally rendered GitBook on `http://localhost:4000`.

### Contribution

* We use branches to isolate the modifications to different chapters. Please send the PR
  to the proper branch you made your modifications to.
* Please test your modifications using the `Vagrantfile` provided. Later TravisCI will also run
  some tests on the repository to avoid problems.



