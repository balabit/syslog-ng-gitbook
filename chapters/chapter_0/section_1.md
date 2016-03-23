# Debian and Ubuntu

##### written by Laszlo Budai

[ref:obs-lbudai-36]: https://build.opensuse.org/project/show/home:laszlo_budai:syslog-ng-3.6
[ref:obs-lbudai-37]: https://build.opensuse.org/project/show/home:laszlo_budai:syslog-ng

## Introduction

This chapter describes how you can install syslog-ng on Debian and on Ubuntu
operating systems from our APT repository.

## syslog-ng

## Install syslog-ng from APT repository

The syslog-ng team has an unofficial APT repository hosted by OBS for Debian and Ubuntu.
Available versions in the OBS repository :
 * 3.6.4
 * 3.7.1
 * 3.7.2
 * 3.7.3

The packaging structure following the original one was created by algernon for Debian systems.
This is basically a modular packaging strategy.

Repositories are available [here][ref:obs-lbudai-36] and [here][ref:obs-lbudai-37] .

### Supported Debian and Ubuntu releases
 * Debian 7.0 (without systemd)
 * Debian 8.0
 * Ubuntu 12.04 (without systemd)
 * Ubuntu 14.04
 * Ubuntu 14.10
 * Ubuntu 15.04
 * Ubuntu 15.10 (available from 3.7.3)

### Available modules (for both 3.6 and 3.7)
 * syslog-ng-mod-amqp
 * syslog-ng-mod-geoip
 * syslog-ng-mod-graphite
 * syslog-ng-mod-journal
 * syslog-ng-mod-json
 * syslog-ng-mod-mongodb
 * syslog-ng-mod-redis
 * syslog-ng-mod-riemann
 * syslog-ng-mod-smtp
 * syslog-ng-mod-sql
 * syslog-ng-mod-stomp

### Modules available only for 3.7.1
 * syslog-ng-mod-java
 * syslog-ng-mod-elastic
 * syslog-ng-mod-hdfs
 * syslog-ng-mod-http
 * syslog-ng-mod-kafka

### Available modules from syslog-ng Incubator for the 3.6 series
 * syslog-ng-mod-basicfuncs-plus
 * syslog-ng-mod-java
 * syslog-ng-mod-trigger
 * syslog-ng-mod-rss
 * syslog-ng-mod-perl
 * syslog-ng-mod-python
 * syslog-ng-mod-kafka
 * syslog-ng-mod-lua

### Modules for 3.7 are not available currently, we are working on that

### Example
  1. get release key

  ```
  wget -qO -  http://download.opensuse.org/repositories/home:/laszlo_budai:/syslog-ng/Debian_8.0/Release.key | sudo apt-key add -
  ```

  2. add repo to APT sources

  ```
  /etc/apt/sources.list.d/syslog-ng-obs.list
  deb  http://download.opensuse.org/repositories/home:/laszlo_budai:/syslog-ng/Debian_8.0 ./
  apt-get update
  apt-get install syslog-ng-core
  ```

You can replace `Debian_8.0` to any of the supported systems.
For Ubuntus there is a 'x' prefix, so the possible values are:

  * `Debian_7.0`
  * `Debian_8.0`
  * `xUbuntu_12.04`
  * `xUbuntu_14.04`
  * `xUbuntu_14.10`
  * `xUbuntu_15.04`
  * `xUbuntu_15.10` (from 3.7.3)

