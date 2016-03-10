# FeeBSD
##### written by Peter Czanik

[ref:compile]: chapters/chapter_2/README.md
[ref:run]: chapters/chapter_2/README.md
[ref:docs]: http://www.balabit.com/sites/default/files/documents/syslog-ng-ose-latest-guides/en/syslog-ng-ose-guide-admin/html-single/index.html
[gh:ose-official]: http://www.github.com/balabit/syslog-ng
[ref:freshports]: http://www.freshports.org/search.php?query=syslog-ng&search=go&num=10&stype=name&method=match&deleted=excludedeleted&start=1&casesensitivity=caseinsensitive
[ref:handbook]: https://www.freebsd.org/doc/handbook/

## Introduction

The syslog-ng application has been available in FreeBSD ports for many years. Recently, thanks
to the hard work of the FreeBSD team, syslog-ng is also available as a ready-to-install package.

The default configuration for `syslog-ng` in ports contains only the most
important dependencies. If you use a package, this is how your package is
configured. This covers the needs of most syslog-ng users. If you need a
specific feature not available with the default configuration in ports, you need
to compile syslog-ng yourself.

The following list shows the available syslog-ng and related ports in FreeBSD,
by the time of writing this chapter:
 * syslog-ng: the latest stable version (not necesseraly a .1 :-) )
 * syslog-ng-devel: the latest development version (alpha/beta and usually .1 too...)
 * syslog-ng-incubator: experimental extensions, to be used together with `syslog-ng`
 * syslog-ng-incubator03
 * syslog-ng33
 * syslog-ng34
 * syslog-ng35
The numbered ports are old, but still receive at least security updates. As most
people in real life, we will use the latest stable version in the rest of this
document.

You can view the current list of available ports by looking into
`/usr/ports/sysutils` and listing `syslog-ng*` or on the web using
[Freshports][ref:freshports]

None of these packages are officially supported by Balabit, but we try to help resolving
problems with our best effort.

## Installing syslog-ng from package

The following command will install `syslog-ng` and all necessary dependencies:

```shell
pkg install syslog-ng
```

*Note:* Installation does not start `syslog-ng` or enables it to start automagically.

## Compiling syslog-ng from ports

These are the minimal steps to compile `syslog-ng` from ports with features and
dependencies you need.

First change to the directory containing `syslog-ng`:
```shell
cd /usr/ports/sysutils/syslog-ng
```

Configure it (enable features & dependencies you need):
```shell
make config
```

Install it:
```shell
make install
```

*Note:* Installation does not start `syslog-ng` or enables it to start automagically.

*Note:* Please consult the [FreeBSD Handbook][ref:handbook] if you are interested in
handling ports and packages in more detail.

## Testing syslog-ng

To test `syslog-ng` you need to stop `syslogd` first, which is bundled with the
base system:

```shell
/etc/rc.d/syslogd stop
```

Then start `syslog-ng`:

```shell
/usr/local/etc/rc.d/syslog-ng onestart
```

```shell
root@fb101r:/usr/ports/sysutils/syslog-ng # logger this is a test
root@fb101r:/usr/ports/sysutils/syslog-ng # tail /var/log/messages
May 19 11:40:38 fb101r pkg-static: syslog-ng-3.6.2_4 installed
May 19 11:56:09 fb101r syslogd: exiting on signal 15
May 19 11:57:02 fb101r syslog-ng[19433]: syslog-ng starting up; version='3.6.2'
May 19 11:57:02 fb101r kernel: <118>May 19 11:56:09 fb101r syslogd: exiting on signal 15
May 19 11:57:18 fb101r root: this is a test
root@fb101r:/usr/ports/sysutils/syslog-ng #
```


## Enable syslog-ng to start by default

Enable `syslog-ng` to start by default with the following two lines appended
to `/etc/rc.conf`:

```shell
syslogd_enable="NO"
syslog_ng_enable="YES
```


*Note:* for more information read the [run first][ref:run] guide.

*Note:* for more information read the syslog-ng [documentation][ref:docs]

