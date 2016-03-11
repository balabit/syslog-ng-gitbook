# Project structure

The following directories are the most substantial ones:

* `lib/`: common source code used by syslog-ng
* `modules/`: each module in syslog-ng has a directory here, like `redis`
* `syslog-ng`: the source code of the `syslog-ng` binary
* `syslog-ng-ctl`: the source code of the `syslog-ng-ctl` command line utility
* `tests`: the home of unit tests and functional tests (but there are tests next to their tested functionality)
