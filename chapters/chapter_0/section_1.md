# Debian and Ubuntu

##### written by Laszlo Budai

[ref:obs-lbudai]: https://build.opensuse.org/project/show/home:laszlo_budai:syslog-ng-3.6

## Introduction

This chapter describes how the user can install syslog-ng on Debian and on Ubuntu
operating systems form our APT repository.

## syslog-ng 3.6.4

## Install syslog-ng from APT repository

The syslog-ng team has an unofficial APT repo hosted by OBS for Debian and Ubuntu.
First release of syslog-ng is available in the OBS repository is 3.6.4.
Packaging structure following the original one created by algernon for Debian systems.
This is basically a modular packaging strategy which we want to keep for the upcoming
syslog-ng-3.7, too. Packaging for 3.7 is still under development.

Repository is available [here][ref:obs-lbudai].

### Supported Debian and Ubuntu releases
 * Debian 7.0 (without systemd)
 * Debian 8.0
 * Ubuntu 12.04 (without systemd)
 * Ubuntu 14.04
 * Ubuntu 14.10
 * Ubuntu 15.04

### Available modules
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

### Available modules from syslog-ng-incubator
 * syslog-ng-mod-basicfuncs-plus
 * syslog-ng-mod-java
 * syslog-ng-mod-trigger
 * syslog-ng-mod-rss
 * syslog-ng-mod-perl
 * syslog-ng-mod-python
 * syslog-ng-mod-kafka
 * syslog-ng-mod-lua

### Example
  1. get release key

  ```
  wget -qO -  http://download.opensuse.org/repositories/home:/laszlo_budai:/syslog-ng-3.6/Debian_8.0/Release.key | sudo apt-key add -
  ```

  2. add repo to APT sources

  ```
  /etc/apt/sources.list.d/syslog-ng-obs.list
  deb  http://download.opensuse.org/repositories/home:/laszlo_budai:/syslog-ng-3.6/Debian_8.0 ./
  apt-get update
  apt-get install syslog-ng-core=3.6.4-1
  ```

You can replace `Debian_8.0` to any of the supported systems.
For Ubuntus there is a 'x' prefix, so the possible values are:

  * `Debian_7.0`
  * `Debian_8.0`
  * `xUbuntu_12.04`
  * `xUbuntu_14.04`
  * `xUbuntu_14.10`
  * `xUbuntu_15.04`

