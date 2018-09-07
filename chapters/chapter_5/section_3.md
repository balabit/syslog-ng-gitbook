# Writing an Apache Kafka module in Python

Apache Kafka is a hugely popular free and open source message broker project. It employs a publish-subscribe messaging model, and can handle hundreds of megabytes of reads and writes per second from thousands of clients. In this section, you will learn how to create a Python destination for syslog-ng, which takes messages and publishes them to Kafka. This tutorial assumes you have a basic understanding of Python and Kafka, and also that you have read the section "Getting started with implementing Python destinations"

###The syslog-ng configuration file

To create a Python destination, you will have to specify the destination in your syslog-ng configuration file.

The following example demonstrates a Python destination in the configuration file:

```c

destination python_to_kafka {
            python(
                class("pythonkafka.KafkaDestination")
                on-error("fallback-to-string")

                host("127.0.0.1")
		port("9092")
                topic("testtopic")
                value-pairs(scope(rfc5424))
	        );
                };

```

You will see that this destination takes the options `host()`, `port()`, and `topic()`. These are not specifically coded into syslog-ng's Python interface. The Python module of syslog-ng allows you to pass arbitrary options from the configuration file into Python, each as a name-value pair. They are combined into a single dictionary and sent to your Python script's "init" function (not "__init__" or any other variation thereof).

Kafka works by grouping messages by topics. Clients can pull messages from topics of their choosing. By specifying a topic, you can specify which clients receive which messages.


This example requires the Python client for Apache Kafka library "kafka-python", which can be found at https://github.com/mumrah/kafka-python/ . To install this library, use the command `pip install kafka-python`.


#### Example: Python file ####

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
        pass

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
#### Example: syslog-ng configuration file ####
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

                host("127.0.0.1")
		port("9092")
                topic("testtopic")

                value-pairs(scope(rfc5424))
	        );
                };


log {
    source(s_local);
    destination(python_to_kafka);
};

```


### Testing
To test the message sending capabilities, follow the instructions in Apache's [official Kafka documentation](http://kafka.apache.org/documentation.html#gettingStarted).
