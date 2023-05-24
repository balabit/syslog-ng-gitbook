# macOS

[ref:compile]: ../../chapters/chapter_2/README.md
[ref:run]: ../../chapters/chapter_2/README.md
[ref:docs]: http://www.balabit.com/sites/default/files/documents/syslog-ng-ose-latest-guides/en/syslog-ng-ose-guide-admin/html-single/index.html
[ref:homebrew]: http://brew.sh
[ref:homebrew-install]: https://docs.brew.sh/Installation
[ref:criterion]: https://github.com/Snaipe/Criterion
[ref:macos-support]: https://yash6866.gitbook.io/syslog-macos-testing/
[ref:libdbi-update]: https://app.gitbook.com/o/oWQ18053o6OL3PBCTe4e/s/-MaZdBoDvCx_0JwOUICk/~/changes/89/modules/afsql-1#dependencies
[gh:ose-official]: <http://www.github.com/balabit/syslog-ng>

## Introduction

The syslog-ng application has been resurrected on macOS by our developer team.
We hope our product can be useful for Mac users who want to increase the security of their
system through reliable logging.

At present we are not supporting macOS syslog-ng on our [official repository][gh:ose-official] on GitHub.
However, you can compile syslog-ng yourself following this guide.

*Note:* the guide is tested on ARM macOS Ventura 13.4, and Intel macOS Monterey 12.6.6 machines, we do our bests to keep it update, but your actual system may require additional steps or slightly different settings.

## Compiling from source

Like every project syslog-ng also uses different libraries and build-systems that must be installed
for compiling and running properly. These dependencies can be satisfied by compiling every-each libs and tools manually, but it might be preferred to do it the easy way. [Homebrew][ref:homebrew] is a package manager for macOS that has great community and support. You can also use it to install the dependencies you need.

### Dependencies

1. [Install Homebrew][ref:homebrew-install] on your system.

   *Hint:* Don't forget to add homebrew to your path, follow the instructions in your terminal!

   *Note:* This will install **Command Line Tools for Xcode** as well if not already prresented on the system that would also be required anyway for a seamless syslog-ng build.
2. Perform `brew update` if you have not done it yet.
3. The following packages should be installed for syslog-ng:
    * automake
    * autoconf
    * autoconf-archive
    * binutils
    * bison
    * flex
    * glib
    * ivykis
    * json-c
    * libtool
    * pcre
    * pkg-config
    * openssl
4. The following package might be needed too depending on your macOS version and architecture:
    * net-snmp
5. The extra modules would require the following
    * hiredis
    * ~~libdbi~~ - See bellow!
    * libmaxminddb
    * libnet
    * librdkafka
    * mongo-c-driver
    * python3
    * rabbitmq-c
    * riemann-client

```shell
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"

brew update

brew install \
    automake \
    autoconf \
    autoconf-archive \
    binutils \
    bison \
    flex \
    glib \
    ivykis \
    json-c \
    libtool \
    pcre \
    pkg-config \
    openssl \
    #
    net-snmp \
    #
    hiredis \
    # libdbi - Do not use the homebrew provided one, see bellow!
    libmaxminddb \
    libnet \
    librdkafka \
    mongo-c-driver \
    python3 \
    rabbitmq-c \
    riemann-client
```

*Note:*

* bison is required to be installed when using homebrew, because the options provided by Apple Developer Tools are incomplete. (for example: missing -W option) The reason is why bison is required to be installed from homebrew is that the -W option is supported only after 2.3.
* net-snmp might be needed as well when using homebrew, because the options provided by Apple Developer Tools are bogus a bit. The reason is why net-snmp might be required from homebrew is that the by default provided pkgconfig might give back bogus lib and include values.
* openssl - since macOS provides LibreSSL by default, we need to expand the search path of pkg-config to find the freshly installed openSSL, see bellow.
* libdbi and libdbi-drivers are [maintained and updated][ref:libdbi-update] in syslog-ng OSE repositories, use the latest master version from there
* actual state of supported features, and the required dependencies can also be found [here][ref:macos-support].

### Preparations

1. Depending your macOS architecture homebrew is using different location for storing its data, so worth using a generic reference to it

   ```shell
   export HOMEBREW_PREFIX=$(brew --prefix)
   ```

2. Force the building process to use bison and net-snmp installed through homebrew instead of provided by Apple Developer Tools.

   * *Option 1:* add bison to `$PATH`

   ```shell
   export PATH=${HOMEBREW_PREFIX}/opt/bison/bin:${HOMEBREW_PREFIX}/opt/net-snmp/bin:${PATH}
   ```

   * *Option 2:* when configuring set the environmental variable `$YACC` to bison

   ```shell
   export YACC=${HOMEBREW_PREFIX}/opt/bison
   ```

3. Extend the search path of pkg-config to use the homebrew version of openssl and net-snmp

   ```shell
   export PKG_CONFIG_PATH=${HOMEBREW_PREFIX}/opt/openssl/lib/pkgconfig:${HOMEBREW_PREFIX}/opt/net-snmp/lib/pkgconfig:${PKG_CONFIG_PATH}
   ```

### Getting the source

To get the latest master from syslog-ng git you can use

```shell
cd YOUR_PREFERRED_WORKING_DIR   # Replace `YOUR_PREFERRED_WORKING_DIR` with your actual preferred working dir 
git clone https://github.com/syslog-ng/syslog-ng . 
```

### Configuration

```shell
./autogen.sh
./configure --with-ivykis=system --disable-java
```

For a full feature set (excluded the not yet supported modules on macOS):

```shell
./autogen.sh
./configure --with-ivykis=system --enable-all-modules --disable-smtp --disable-mqtt --disable-java --enable-tests --enable-manpages
```

*Note:*

* for various reasons not all modules can be configured, built and used on all macOS versions and architectures
* for using all the available modules you might have to install further dependencies

   For more details please see the [actual state of supported features, and the required dependencies][ref:macos-support].

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

*Note:* for more information read the [run first][ref:run] guide and the syslog-ng [documentation][ref:docs]


