# Getting started with implementing Python destinations

Python is a popular easy-to-use, high-level language which makes writing code fun and easy. Syslog-ng supports writing destinations in python, allowing you to easily extend the capabilities of syslog-ng for your own needs. In this section, you will learn how to create a python destination for syslog-ng which takes messages and logs them to a file. This tutorial assumes a basic understanding of python.

###The syslog-ng config file

To create a python destination, you will need to specify the destination in your syslog-ng configuration file.

Here is an example of a python destination in the config file:

```c
destination python_to_file {
            python(
                class("betterpythonexample.TextDestination")
                on-error("fallback-to-string")
                value-pairs(scope(everything))
                );
                };
```

You will see that python destinations require three parameters: Class, on-error, and value-pairs. Refer to the syslog-ng OSE documentation for a more thorough explanation of these

#### Class

The syntax for the class parameter is filename-without-extension.ClassName

#### on-error

Specifies what to do when a message can't be properly parsed. 

#### Value-pairs

Specifies which name-value pairs will be generated from the message and passed in a dictionary to the python script



###The LogDestination class

To interface with syslog-ng, you will need a class with these methods:

```python
    def open(self):
        """Open a connection to the target service"""
        """Should return False if opening fails"""
        return True

    def close(self):
        """Close the connection to the target service"""
        pass

    def is_opened(self):
        """Check if the connection to the target is able to receive messages"""
        """Should return False if target is not open"""
        return True

    def init(self):
        """This method is called at initialization time"""
        """Should return false if initialization fails"""
        return True

    def deinit(self):
        """This method is called at deinitialization time"""
        pass

    def send(self, msg):
        """Send a message to the target service

        It should return True to indicate success, False will suspend the
        destination for a period specified by the time-reopen() option."""
        pass
```

When syslog-ng starts, it will attempt to run the init method. This method should do any initialization that needs to be done at the start of the program.

Whenever a new message is generated and fed to your python script, a python dictionary will be passed to the send function with name-value pairs specified in the relevant syslog-ng config file.

To put it all together, here is a sample python class that writes all name-value pairs given to a file, and the accompanying syslog-ng config file.

Python file:

```python

class LogDestination(object):

    def open(self):
        """Open a connection to the target service"""
        return True

    def close(self):
        """Close the connection to the target service"""
        pass

    def is_opened(self):
        """Check if the connection to the target is able to receive messages"""
        return True

    def init(self):
        """This method is called at initialization time"""
        return True

    def deinit(self):
        """This method is called at deinitialization time"""
        pass

    def send(self, msg):
        """Send a message to the target service

        It should return True to indicate success, False will suspend the
        destination for a period specified by the time-reopen() option."""
        pass


class TextDestination(LogDestination):
    def __init__(self):
        self.outfile = None

    def init(self):
        self.outfile = open('/tmp/example.txt', 'a')
        self.outfile.write("initialized\n")
        self.outfile.flush()
        return True
       
    def open(self):
        self.outfile.write("opened\n")
        self.outfile.flush()
        return True

    def close(self):
        self.outfile.write("closed\n")
        self.outfile.flush()
        return True

    def deinit(self):
        self.outfile.write("deinit\n")
        self.outfile.flush()
        self.outfile.close();
        return True

    def send(self, msg):
        self.outfile.write("Name Value Pairs are \n")
        
        for key,v in msg.items():
            self.outfile.write(str(key)+" "+str(v)+"\n");
        self.outfile.flush()
        return True


        
```
Syslog-ng Config File:
```c
#############################################################################
#

@version: 3.7
@include "scl.conf"

source s_local {
	system();
	internal();
};

destination python_to_file {
            python(
                class("betterpythonexample.TextDestination")
                on-error("fallback-to-string")
                value-pairs(scope(everything))
                );
                };

log {
    source(s_local);
    destination(python_to_file);
};

```