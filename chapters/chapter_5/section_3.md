# Writing an Apache Kafka module in Python

Apache Kafka is a hugely popular Free and Open Source message broker project. It employs a publish-subscribe messaging model, and can handle hundreds of megabytes of reads and writes per second from thousands of clients. In this section, you will learn how to create a Python destination for syslog-ng which takes messages and publishes them to Kafka. This tutorial assumes you have a basic understanding of Python and Kafka, and also that you have read the section "Getting started with implementing Python destinations"

###The syslog-ng config file

To create a python destination, you will need to specify the destination in your syslog-ng configuration file.

Here is an example of a python destination in the config file:

```c

destination python_to_kafka {
            python(
                class("pythonkafka.KafkaDestination")
                on-error("fallback-to-string")

                option("host","127.0.0.1")
		option("port","9092")
                option("topic","testtopic")
                value-pairs(scope(rfc5424))
	        );
                };

```

You will see that this destination takes three "option" parameters. Syslog-ng's python module allows you to pass multiple options, each as a name-value pair. They are combined into a single dict and sent to your python script's "init" function (not "__init__" or any other variation thereof).

Kafka works by grouping messages by topic. Clients can pull messages from topics of their choosing. By specifying topic, you can specify which clients get which messages.


This example requires the python kafka library "kafka-python", which can be found at https://github.com/mumrah/kafka-python/ . To install this library, you can simply use the command "pip install kafka-python".


With that in mind, here is the python script you need.
Python file:

```python
import requests
from kafka.producer import SimpleProducer
from kafka.client import KafkaClient
import kafka.common
from kafka.common import LeaderNotAvailableError

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

    def init(self,args):
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

class KafkaDestination(LogDestination):

    def __init__(self):
        self.host = None
        self.port = None
        self.kafka_client = None
        self.kafka_producer = None
        self.topic = None
        self.is_available = None

    def init(self,args):
        print args
        try:
            self.host=args["host"]
            self.port=args["port"]
            self.topic=args["topic"]
        except KeyError:
            return False
        self.kafka_client = KafkaClient(self.host, self.port)
        self.kafka_producer = SimpleProducer(self.kafka_client)
        return True

    def open(self):
        return True

    def close(self):
        self.kafka_producer.stop()
        return True

    def deinit(self):
        return True

    def send(self, msg):
        msg_string=str(msg)
        try:
            print msg.values()
            print(self.kafka_producer.send_messages(self.topic,msg_string))
        except LeaderNotAvailableError:
            try:
                time.sleep(1)
                print_response(self.kafka_producer.send_messages(self.topic,msg_string))
            except:
                return False
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

destination python_to_kafka {
            python(
                class("pythonkafka.KafkaDestination")
                on-error("fallback-to-string")

                option("host","127.0.0.1")
		option("port","9092")
                option("topic","test")
                value-pairs(scope(rfc5424))
	        );
                };


log {
    source(s_local);
    destination(python_to_kafka);
};

```


### Testing
To test the message sending capabilities, follow the instructions on Apache's [official kafka documentation](http://kafka.apache.org/documentation.html#gettingStarted).