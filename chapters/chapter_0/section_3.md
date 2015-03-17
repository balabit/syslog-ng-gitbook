# MacOS X platform

[ref:compile]: chapters/chapter_2/README.md
[ref:run]: chapters/chapter_2/README.md
[ref:docs]: http://www.balabit.com/sites/default/files/documents/syslog-ng-ose-latest-guides/en/syslog-ng-ose-guide-admin/html-single/index.html
[ref:homebrew]: http://brew.sh
[gh:ose-official]: http://www.github.com/balabit/syslog-ng
[gh:ose-gregory094]: http://www.github.com/gregory094/syslog-ng

## Introduction

Syslog-ng has been resurrected on OSX platform by our developer team.
We hope our product can be useful for Mac users who want security on their
system via reliable logging. 

At present we support syslog-ng 3.6 on our [official repository][gh:ose-official] on GitHub and 3.7 also planned to be available
on OSX platform. A “non-official” support is available for 3.5 at [gregory094/syslog-ng][gh:ose-gregory094] 
on GitHub but we do not plan to backport the support officially.

## Installation process
Like every project syslog-ng also uses different libraries and build-systems that must be installed
for compiling and running properly. These dependencies can be satisfied compiling every-each libs and tools
with our own hands but I would prefer to do it on the easy way. [Homebrew][ref:homebrew] is a package manager for OSX
that has great community and support. We can also use it to install the dependencies we needed.

### Dependencies
1. Install homebrew on your system.
2. Do `brew update` if you haven’t done it yet.
3. The following packages should be installed for syslog-ng:
    * glib
    * openssl
    * libtool
    * automake
    * pkgconfig
    * eventlog
    * pcre
    * bison

```shell
ruby -e “$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)”
brew update
brew install glib openssl libtool automake pkgconfig eventlog pcre bison
```

*Note:* bison is needed to be installed using homebrew for the options provided by Apple Developer Tools are
incomplete. (e.g.: missing -W option) The reason is why bison is needed to be installed from homebrew is
that -W option is supported only after 2.3.

### Preparations

1. Disable syslogd, the official logging service of Apple. It is not a necessary step but using two logger
services doesn’t make sense.
2. Force building process to use bison installed via homebrew instead of provided by Apple Developer Tools.
    * *Option 1:* add bison to `$PATH`
    * *Option 2:* when configuring set the environmental variable `$YACC` to bison

### Compile and install

In the syslog-ng folder declare the command below:

```shell
./configure && make && make install
```

*Note:* for options and more read [compile first][ref:compile] guide.

### Testing

In order to run the tests use the command below:

```shell
make dist-check VERBOSE=1
make func-test VERBOSE=1
```

*Note:* for more read [compile first][ref:compile] guide.

### Run

```shell
./syslog-ng
```

*Note:* for more read [run first][ref:run] guide.

*Note:* for more read syslog-ng [documentation][ref:docs]


