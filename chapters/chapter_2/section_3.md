# testing

## make check

Actually, you just have to run `make check`. This will compile and execute the unit
tests. If everything is OK, you should see something like this:

```
============================================================================
Testsuite summary for syslog-ng 3.8.0alpha0
============================================================================
# TOTAL: 82
# PASS:  82
# SKIP:  0
# XFAIL: 0
# FAIL:  0
# XPASS: 0
# ERROR: 0
============================================================================
```

If something goes wrong, check the logs of the tests (`test-suite.log`). You can debug
the failing unit test with a debugger.

## make distcheck

`make distcheck` is very similar to `make check`, but it also ensures that
the distribution tarball can be properly used.
