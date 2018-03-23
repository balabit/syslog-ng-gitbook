# macOS

[ref:compile]: ../../chapters/chapter_2/README.md
[ref:run]: ../../chapters/chapter_2/README.md
[ref:docs]: http://www.balabit.com/sites/default/files/documents/syslog-ng-ose-latest-guides/en/syslog-ng-ose-guide-admin/html-single/index.html
[ref:homebrew]: http://brew.sh
[ref:criterion]: https://github.com/Snaipe/Criterion
[gh:ose-official]: http://www.github.com/balabit/syslog-ng

## Introduction

The syslog-ng application has been resurrected on macOS by our developer team.
We hope our product can be useful for Mac users who want to increase the security of their
system through reliable logging.

At present we are not supporting macOS syslog-ng on our [official repository][gh:ose-official] on GitHub.
However, you can compile syslog-ng yourself following this guide.

## Compiling from source
Like every project syslog-ng also uses different libraries and build-systems that must be installed
for compiling and running properly. These dependencies can be satisfied by compiling every-each libs and tools manually, but it might be preferred to do it the easy way. [Homebrew][ref:homebrew] is a package manager for macOS that has great community and support. You can also use it to install the dependencies you need.

### Dependencies
1. Install Homebrew on your system.
2. Perform `brew update` if you have not done it yet.
3. The following packages should be installed for syslog-ng:
    * automake
    * autoconf
    * binutils
    * glib
    * autoconf-archive
    * flex
    * bison
    * libtool
    * pkg-config
    * ivykis
    * openssl
    * pcre

```shell
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

brew update
brew install \
    automake \
    autoconf \
    binutils \
    glib \
    autoconf-archive \
    flex \
    bison \
    libtool \
    pkg-config \
    ivykis \
    openssl \
    pcre
```

*Note:* bison is required to be installed when using homebrew, because the options provided by Apple Developer Tools are incomplete. (for example: missing -W option) The reason is why bison is required to be installed from homebrew is that the -W option is supported only after 2.3.

### Preparations

1. Force the building process to use bison installed through homebrew instead of provided by Apple Developer Tools.
    * *Option 1:* add bison to `$PATH`
    * *Option 2:* when configuring set the environmental variable `$YACC` to bison
2. Extend the search path of pkg-config.

```shell
export PATH=/usr/local/opt/bison/bin:$PATH
export PKG_CONFIG_PATH=/usr/local/lib/pkgconfig:/usr/local/opt/openssl/lib/pkgconfig
```

### Configuration

```shell
./autogen.sh
./configure --with-ivykis=system
```

For a minimal featureset:
```shell
./autogen.sh
./configure --with-ivykis=system --disable-amqp --disable-mongodb --disable-riemann --disable-java --disable-python
```

### Compile and install

```shell
make -j4
make install
```

Optionally, you can specify the install prefix passing `--prefix /example/installdir/` to the configure script.

*Note:* for options and more information, read the [compile first][ref:compile] guide.

### Testing

In order to run the tests, you have to install the [Criterion][ref:criterion] testing framework (for example: `brew install snaipe/soft/criterion`). Then use the command below:

```shell
make check -j4
```

*Note:* for more read [compile first][ref:compile] guide.

### Run

```shell
./syslog-ng -F
```

*Note:* for more information read the [run first][ref:run] guide.

*Note:* for more information read the syslog-ng [documentation][ref:docs]


