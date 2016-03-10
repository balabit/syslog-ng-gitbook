# openSUSE
##### written by Peter Czanik

[ref:compile]: chapters/chapter_2/README.md
[ref:run]: chapters/chapter_2/README.md
[ref:docs]: http://www.balabit.com/sites/default/files/documents/syslog-ng-ose-latest-guides/en/syslog-ng-ose-guide-admin/html-single/index.html
[gh:ose-official]: http://www.github.com/balabit/syslog-ng
[ref:obs-czp-sub]: https://build.opensuse.org/project/subprojects/home:czanik

## Introduction

The syslog-ng application has been available in openSUSE and SLES for many years. The included
version usually lags behind a version or more. Up to date syslog-ng packages for
recent openSUSE and SLES releases are available in the [OBS repositories of Peter Czanik][ref:obs-czp-sub]. Depending on the distribution release, syslog-ng, Rsyslog or
systemd's journald (package `systemd-logger`) are installed as the default logging
solution.

None of these packages are officially supported by Balabit, but we try to help resolving
problems with our best effort.

## Using the latest syslog-ng version

If you want to install the latest available syslog-ng version, add one of the [OBS repositories of Peter Czanik][ref:obs-czp-sub] first. For version 3.6 use the following command:
```shell
zypper ar http://download.opensuse.org/repositories/home:/czanik:/syslog-ng36/openSUSE_13.2/ syslog-ng36
```
This command line refers to the latest distribution of syslog-ng versions at the
time of writing. You might need to change either one or both version numbers.
You can skip this step, if you do not need the latest syslog-ng version.

## Checking available subpackages

The syslog-ng package on openSUSE is organized into a core package called `syslog-ng`
and sub packages with extra dependencies. You can search for a full list
of packages using `zypper`:

```shell
linux-uv4b:~ # zypper se syslog-ng
Loading repository data...
Reading installed packages...

S | Name            | Summary                          | Type   
--+-----------------+----------------------------------+--------
  | syslog-ng       | The new-generation syslog-daemon | package
  | syslog-ng-devel | Development files for syslog-ng  | package
  | syslog-ng-geoip | GeoIP support                    | package
  | syslog-ng-json  | JSON output support              | package
  | syslog-ng-redis | Redis destination support        | package
  | syslog-ng-smtp  | SMTP output support              | package
  | syslog-ng-sql   | SQL support using DBI            | package
```

## Installation

Choose the package(s) you need and install them:

```shell
zypper -v in syslog-ng syslog-ng-json
```

There will be a conflict, as by default logging to `journald` is enabled. The
`systemd-logger` package can be safely deleted: choose number one.

```shell
 Solution 1: deinstallation of systemd-logger-210-25.16.1.x86_64
```

## Starting syslog-ng

You can start `syslog-ng` many ways:

```shell
systemctl start syslog
```

is often called by openSUSE guys as:

```shell
rcsyslog start
```

*Note:* it is referred to as `syslog` in init scripts, because it is a wrapper among
different syslog implementations.

## Testing syslog-ng

```shell
linux-uv4b:~ # logger this is a test
linux-uv4b:~ # tail /var/log/messages 
May 15 17:21:51 linux-uv4b syslog-ng[1831]: syslog-ng starting up; version='3.5.6'
May 15 17:27:38 linux-uv4b root: this is a test
```

*Note:* for more information, read the [run first][ref:run] guide.



