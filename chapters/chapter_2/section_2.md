# compile

I'll demonstrate the building steps on the upstream repository, but you can apply these steps
on your forked repository as well.

## building

1. Clone your forked repository locally

 ```
git clone https://github.com/balabit/syslog-ng.git
```

2. Step into the directory `syslog-ng` directory and run `autogen.sh`:

 ```
./autogen.sh
```

 This script will clone the git submodules and initialize the build system. The
result of the execution should be a `configure` script.

3. Create build directory
We prefer to build syslog-ng in a dedicated directory, so your git repo is kept
tidy.

 ```
mkdir build
cd build
```

4. Run the `configure` scipt:

 ```
../configure --enable-debug --prefix=$HOME/install/syslog-ng
```

 You can pass additional parameters to configure, but these are the most common ones.
If you run `../configure --help` you can see all the valid parameters.
The result of the configure process is several new `Makefile` in your build directory.

5. Run `make`:

 ```
make -j
```

 The `-j` flag will parallelize the compilation process. If `make` works for you (without `-j`)
but `make -j` not, that's a bug.

You should have a freshly built syslog-ng by the end of this step.

## cleanup

 You can execute `make clean` to remove the build artifacts. `make distclean` will also
remove the `configure` script. You can also completely remove the content of your build directory.
