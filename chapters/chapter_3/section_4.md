# Building from source on macOS

[ref:compile-first]: /chapters/chapter_2/section_2
[ref:testing-first]: /chapters/chapter_2/section_3
[ref:run]: /chapters/chapter_3
[ref:docs]: http://www.balabit.com/sites/default/files/documents/syslog-ng-ose-latest-guides/en/syslog-ng-ose-guide-admin/html-single/index.html
[ref:homebrew]: http://brew.sh
[ref:homebrew-install]: /chapters/chapter_0/section_3
[ref:homebrew-install-detailed]: https://mac.install.guide/homebrew/3.html
[ref:homebrew-ose-install]: /chapters/chapter_0/section_3/
[ref:criterion]: https://github.com/Snaipe/Criterion
[ref:macos-support]: https://syslog-macos-testing.gitbook.io/syslog-macos-testing
[ref:libdbi-update]: https://syslog-macos-testing.gitbook.io/syslog-macos-testing/modules/afsql-1#dependencies
[gh:ose-official]: <http://www.github.com/balabit/syslog-ng>

## Introduction

The syslog-ng application has been resurrected on macOS by our developer team.
We hope our product can be useful for Mac users who want to increase the security of their
system through reliable logging.

At present we are not supporting macOS syslog-ng on our [official repository][gh:ose-official] on GitHub.
However, you can compile syslog-ng yourself following this guide.

> [!NOTE]
The guide is tested on ARM macOS Sonoma 14.2.1, Ventura 13.4, and Intel macOS Monterey 12.6.6 machines, we do our bests to keep it update, but your actual system may require additional steps or slightly different settings.

## Compiling from source

Like every project syslog-ng also uses different libraries and build-systems that must be installed
for compiling and running properly. These dependencies can be satisfied by compiling every-each libs and tools manually, but it might be preferred to do it the easy way. [Homebrew][ref:homebrew] is a package manager for macOS that has great community and support. You can also use it to install the dependencies you need.

### Dependencies

1. [Install Homebrew][ref:homebrew-install] on your system.

   > Tip:
   > Don't forget to set up the homebrew environment, follow the instructions in your terminal! [Here][ref:homebrew-install-detailed] you can find an even more detailed instruction about the topic.

   > Note:
   > This will install **Command Line Tools for Xcode** as well if not already presented on the system that would also be required anyway for a seamless syslog-ng build.
2. Perform `brew update` if you have not done it yet.
3. The following packages should be installed for syslog-ng:
    * autoconf
    * autoconf-archive
    * automake
    * bison
    * flex
    * glib
    * ivykis
    * json-c
    * libtool
    * openssl
    * pcre
    * pkg-config
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
6. Extra tools you might require
    * cmake
    * criterion
    * gcc@11

> [!TIP]
If you you have [syslog-ng installed via brew][ref:homebrew-ose-install], as a reference, you can check the dependencies of the brew built version [like this][ref:homebrew-ose-install]

This is how it might look like if you start from the ground:

```shell
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"

eval "$(brew shellenv)"

brew update

brew install \
    autoconf \
    autoconf-archive \
    automake \
    bison \
    flex \
    glib \
    ivykis \
    json-c \
    libtool \
    net-snmp \
    openssl \
    pcre \
    pkg-config \
    # Optional syslog-ng module dependencies
    hiredis \
    # Do not use the homebrew provided one, see bellow!
    # libdbi 
    libmaxminddb \
    libnet \
    librdkafka \
    mongo-c-driver \
    python3 \
    rabbitmq-c \
    riemann-client
    # Optional development modules
    # cmake - Optional, a better replacement of autotools making system
    # criterion - Optional, needed for unit testing
    # gcc@11 - Optional, clang now should compile all modules nicely
```

> [!NOTE]
>
>* bison is required to be installed when using homebrew, because the options provided by Apple Developer Tools are incomplete. (for example: missing -W option) The reason is why bison is ?>required to be installed from homebrew is that the -W option is supported only after 2.3.
>* net-snmp might be needed as well when using homebrew, because the options provided by Apple Developer Tools are bogus a bit. The reason is why net-snmp might be required from homebrew is that the by default provided pkgconfig might give back bogus lib and include values.
>* openssl - since macOS provides LibreSSL by default, you might need to expand the search path of pkg-config to find the freshly installed openSSL, see bellow. (seems it was an issue only with 1.1.x version of openssl)
>* libdbi and libdbi-drivers are [maintained and updated][ref:libdbi-update] in syslog-ng OSE repositories, use the latest master version from there
>* actual state of supported features, and the required dependencies can also be found [here][ref:macos-support].

### Preparations

1. Depending your macOS architecture and version homebrew is using different location for storing its data, so worth using generic references to it, for this, [just follow the instructions][ref:homebrew-install-detailed]] during homebrew installastion.

   In a nutshell, you either have to use `brew shellenv`, or set manually the env like this

   ```shell
   export HOMEBREW_PREFIX=$(brew --prefix)
   export HOMEBREW_CELLAR=${HOMEBREW_PREFIX}/Cellar
   export HOMEBREW_REPOSITORY=${HOMEBREW_PREFIX}
   export MANPATH=${HOMEBREW_PREFIX}/share/man:${MANPATH}
   export INFOPATH=${HOMEBREW_PREFIX}/share/info:${INFOPATH}
   export PATH=${HOMEBREW_PREFIX}/bin:${HOMEBREW_PREFIX}/sbin:${HOMEBREW_PREFIX}/opt/python/libexec/bin:$PATH
   ```

2. Force the building process to use bison, net-snmp (and libnet if) installed through homebrew instead of provided by Apple Developer Tools and macOS.

   Add them to the `$PATH`

   ```shell
   export PATH=${HOMEBREW_PREFIX}/opt/bison/bin:${HOMEBREW_PREFIX}/opt/libnet/bin:${HOMEBREW_PREFIX}/opt/net-snmp/bin:${PATH}
   ```

3. Extend the search path of pkg-config to use the homebrew version of openssl, net-snmp and pkgconfig

   ```shell
   export PKG_CONFIG_PATH=${HOMEBREW_PREFIX}/opt/openssl/lib/pkgconfig:${HOMEBREW_PREFIX}/opt/net-snmp/lib/pkgconfig:${HOMEBREW_PREFIX}/lib/pkgconfig:${PKG_CONFIG_PATH}
   ```

4. Some of the modules will not, or will incorrectly provide pkg-config support (even if added to PKG_CONFIG_PATH, e.g. libmaxminddb), to help the automatic configurations find them you can add brew to `CFLAGS`, `CPPFLAGS`, and `LDFLAGS`

   ```shell
   export CFLAGS="-I${HOMEBREW_PREFIX}/include/ ${CFLAGS}"
   export CPPFLAGS="${CFLAGS} ${CPPFLAGS}"
   export LDFLAGS="-L${HOMEBREW_PREFIX}/lib ${LDFLAGS}"
   ```
  
   > Note:
   > 
   >It could also happen that you must provide here further library inlcude and lib paths, e.g. for openssl 1.1.x, etc.

5. If you wanted to use `gcc` then to force usage of the brew installed version you might want to add

   ```shell
   ln -s ${HOMEBREW_PREFIX}/bin/gcc-11 ${HOMEBREW_PREFIX}/bin/gcc
   ln -s ${HOMEBREW_PREFIX}/bin/g++-11 ${HOMEBREW_PREFIX}/bin/g++
   ```

   Double check the result

   ```shell
    gcc --version
   ```

   Expect something similar

   ```shell
   gcc (Homebrew GCC 11.4.0) 11.4.0
   ```

   > Note:
   > 
   >The result of the default (clang) one that comes from the output of `/usr/bion/gcc` (which you have by default, and is a simple symlink that points to clang)

   ```shell
   Apple clang version 15.0.0 (clang-1500.1.0.2.5)
   ```

### Getting the source

To get the latest master from syslog-ng git you can use

```shell
cd YOUR_PREFERRED_WORKING_DIR   # Replace `YOUR_PREFERRED_WORKING_DIR` with your actual preferred working dir 
git clone https://github.com/syslog-ng/syslog-ng . 
```

### Select the compiler

For gcc

```shell
export CC=gcc
export CXX=g++
```

> Note:
> Some parts will still be compiled with clang at the moment as gcc cannot compile e.g. the latest ObjectivC sources syslog-ng uses

For clang (optional, macOS default)

```shell
export CC=clang
export CXX=clang++
```

### Configuration

#### Using autotool

```shell
./autogen.sh

# it is always a good idea keeping as clean the source folder as pissible, so
# use a dedicated build folder for easier cleanup
mkdir build; cd build

# you might want to use --prefix /example/installdir/ as well, see bellow
../configure --with-ivykis=system --with-systemd-journal=no --disable-java --disable-java-modules
```

> [!WARNING]
By a good chance, you might want to install the self built instance first to a custom location to prevent overwriting a possibly already existing brew installation version. In that case pass `--prefix /full_path_of/installdir/` to the `configure` script in the above steps.

For a full feature set you can add further `configure`` flags (excluded the not yet supported modules on macOS), for example

```shell
../configure --enable-all-modules --with-ivykis=system --with-systemd-journal=no --disable-java --disable-java-modules --disable-smtp --disable-mqtt --disable-pacct --disable-grpc    
```

> [!NOTE]
>
>* for various reasons not all modules can be configured, built and used on all macOS versions and architectures
>* for using all the available modules you might have to install further dependencies

For more details please see the [actual state of supported features, and the required dependencies][ref:macos-support].

#### Using cmake

For the full (currently) feature set you can use

```shell
cmake --install-prefix /full_path_of/installdir -B build . -Wno-dev -DIVYKIS_SOURCE=system -DENABLE_JAVA=OFF -DENABLE_JAVA_MODULES=OFF -DENABLE_PYTHON=ON -DENABLE_PYTHON_MODULES=ON -DBUILD_TESTING=OFF -DENABLE_AFSMTP=OFF -DENABLE_MQTT=OFF -DENABLE_PACCT=OFF -DENABLE_CPP=ON -DENABLE_GRPC=OFF --fresh 
```

### Compile and install

#### autotools

```shell
# add AM_DEFAULT_VERBOSITY=1 before -j4 option for detailed compilation logging
make -j4
make install

# or, in a single line
# make -j4 install
```

> [!NOTE]
For options and more information, read the [compile first][ref:compile-first] guide.

#### cmake

```shell
# add -v as well for detailed compilation logging
cmake --build build/. --target install -j4
```

### Testing

In order to run the tests, you have to install first the [Criterion][ref:criterion] testing framework (for example: `brew install criterion`), and re-[configure](#configuration) the build.
After that use the command below:

```shell
make check -j4
```

> [!NOTE]
For more read [testing first][ref:testing-first] guide.

### Run

```shell
./syslog-ng -F
```

> [!NOTE]
For more information read the [run first][ref:run] guide and the syslog-ng [documentation][ref:docs]
