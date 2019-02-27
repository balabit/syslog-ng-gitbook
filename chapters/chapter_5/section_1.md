# Getting started with implementing Python destinations

Python is a popular, easy-to-use, high-level language that makes writing code fun and easy. The syslog-ng application supports writing destinations in Python, allowing you to easily extend the capabilities of syslog-ng for your own needs. In this section, you will learn how to create a Python destination for syslog-ng, which takes messages and logs them to a file. This tutorial assumes a basic understanding of Python.

###The syslog-ng configuration file

To create a Python destination, you will need to specify the destination in your syslog-ng configuration file.

The following example demonstrates a Python destination in the configuration file:

```c
destination d_python_to_file {
    python(
        class("pythonexample.TextDestination")
        on-error("fallback-to-string")
        value-pairs(scope(everything))
        options(my_sample_option option_value)
    );
};
```

You will see that the Python destination requires three options: `class()`, `on-error()`, and `value-pairs()`. Refer to the syslog-ng OSE documentation for a more thorough explanation of these options. The `options()` part is optional. The Python destination driver will receive these values during initialization.

#### class()

The syntax for the class parameter is `<filename-without-extension>.<ClassName>`.

#### on-error()

Specifies what to do when a message cannot be properly parsed.

#### value-pairs()

Specifies which name-value pairs will be generated from the message and passed in a dictionary to the Python script.

You can also include other arbitrary options in the configuration file. These will be sent to Python in the form of a dictionary. Check out the chapter "Writing an Apache Kafka module in Python" if you want to learn more about this topic.

###The LogDestination class

To interface with syslog-ng, you will need a class with these methods:

```python
    def open(self):
        """Open a connection to the target service

        Should return False if opening fails"""
        return True

    def close(self):
        """Close the connection to the target service"""
        pass

    def is_opened(self):
        """Check if the connection to the target is able to receive messages

        Should return False if target is not open"""
        return True

    def init(self, options):
        """This method is called at initialization time

        Should return False if initialization fails"""
        return True

    def deinit(self):
        """This method is called at deinitialization time"""
        pass

    def send(self, msg):
        """Send a message to the target service

        It should return True to indicate success, False will suspend the
        destination for a period specified by the time-reopen() option."""
        return True
```

When syslog-ng starts, it will attempt to run the init method. This method should do any initialization that needs to be performed at the start of the program.

Whenever a new message is generated and fed to your Python script, a Python dictionary is passed to the sent function with name-value pairs specified in the relevant syslog-ng configuration file.

The following two examples put it all together. A sample python class that writes all name-value pairs given to a file, and the accompanying syslog-ng configuration file.

#### Example: Python file ####

(Filename: `pythonexample.py`.)

```python
class LogDestination(object):

    def open(self):
        """Open a connection to the target service

        Should return False if opening fails"""
        return True

    def close(self):
        """Close the connection to the target service"""
        pass

    def is_opened(self):
        """Check if the connection to the target is able to receive messages"""
        return True

    def init(self, options):
        """This method is called at initialization time

        Should return false if initialization fails"""
        return True

    def deinit(self):
        """This method is called at deinitialization time"""
        pass

    def send(self, msg):
        """Send a message to the target service

        It can return boolean. Since 3.20, it can return integer
        alternatively.
        Boolean: True to indicate success, False will suspend the
        destination for a period specified by the time-reopen() option.
        After that the same message is retried until retries() times.

        Integer:
        self.SUCCESS: message sending was successful (same as boolean True)
        self.ERROR: message sending was unsuccessful. Same message is retried.
            (same as boolean False)
        self.DROP: message cannot be sent, it should be dropped immediately.
        self.QUEUED: message is not sent immediately, it will be sent with the flush method.
        self.NOT_CONNECTED: message is put back to the queue, open method will be called until success.
        self.RETRY: message is put back to the queue, try to send again until 3 times, then fallback to self.NOT_CONNECTED."""

        return True


class TextDestination(LogDestination):
    def __init__(self):
        self.outfile = None
        self._is_opened = False

    def init(self, options):
        self.outfile = open("/tmp/example.txt", "a")
        self.outfile.write("initialized with {}\n".format(options))
        self.outfile.flush()
        return True

    def is_opened(self):
        return self._is_opened

    def open(self):
        self.outfile.write("opened\n")
        self.outfile.flush()
        self._is_opened = True
        return True

    def close(self):
        self.outfile.write("closed\n")
        self.outfile.flush()
        self._is_opened = False

    def deinit(self):
        self.outfile.write("deinit\n")
        self.outfile.flush()
        self.outfile.close();

    def send(self, msg):
        self.outfile.write("Name Value Pairs are:\n")

        for key,v in msg.items():
            self.outfile.write(str(key) + " = " + str(v) + "\n");
        self.outfile.write("________________________\n\n")
        self.outfile.flush()
        return True
```
#### Example: syslog-ng configuration file ####
```c
@version: 3.7
@include "scl.conf"

source s_local {
    system();
    internal();
};

destination d_python_to_file {
    python(
        class("pythonexample.TextDestination")
        on-error("fallback-to-string")
        value-pairs(scope(everything))
        options(my_sample_option option_value)
    );
};

log {
    source(s_local);
    destination(d_python_to_file);
};
```

### Python-specific notes
You must have the folder containing your python class present in the PYTHONPATH directory. In bash, you can add this by typing `export PYTHONPATH=$PYTHONPATH:/path/to/folder`.
