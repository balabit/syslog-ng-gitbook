# Simple Python Source

This section contains examples how to write a python source in syslog-ng.

There are two options available for python source:
- Python fetcher
This option is useful if remote logs need to be fetched by the source. You can use simple blocking server/client libraries to receive/fetch logs.

- Python source
This is a more general source than a python fetcher and it is for non-blocking, event-based implementations, or for any other advanced use cases, where you need more control. For example:

You can implement your own event loop, or integrate an external framework's or library's event loop (Kafka consumer, HTTP server, Flask, Twisted engine).

## Python fetcher
### API
A Python Fetcher implementation must be inherited from `syslogng.LogFetcher` class. There is one mandatory method: `fetch()`
- `fetch()`

The `fetch()` method will be called by syslog-ng whenever syslog-ng is ready to process a new message. This method needs to return a tuple of form (status, syslogng.LogMessage). Status can be `LogFetcher.FETCH_ERROR`, `LogFetcher.FETCH_NOT_CONNECTED`, `LogFetcher.FETCH_SUCCESS`, `LogFetcher.FETCH_TRY_AGAIN` and `LogFetcher.FETCH_TRY_NO_DATA`.

The `LogFetcher.FETCH_ERROR` status will result in a `close()` `open()` call, waiting `time-reopen()` seconds in between.

The `LogFetcher.FETCH_NOT_CONNECTED` will result in an `open()` call after `time-reopen()` seconds in between.

The `LogFetcher.FETCH_SUCCESS` status means the fetch was successful, and syslog-ng can handle the returned message.
The `LogFetcher.FETCH_TRY_AGAIN` status means fetcher cannot provide message this time, but make the source call fetch as soon as possible.
The `LogFetcher.FETCH_NO_DATA` status means there is no data available this time, syslog-ng can wait some time before calling fetch again. The wait time is equal to time-reopen() by default, but it might be overridden if fetch_no_data_delay(sec) is provided.

The following methods are optional: `init()`, `deinit()`, `open()`, `close()`, `request_exit()`

- `request_exit()`

This method is called before syslog-ng stops or reloads. Any blocking calls should be cancelled here.

- `init(options)`

This method is called during initializaton: when syslog-ng starts, or after syslog-ng reloads. If there were options provided in the configuration, they will be available in the sole parameter of `init()`.
The return value is `True`/`False`. If `False` is returned, syslog-ng will not start.

- `deinit()`

This method is called during deinitialization: when syslog-ng stops, or before syslog-ng reloads.

- `open()`

This method can be used to open connection towards the entities, from which the driver needs to fetch logs.

It is called after `init()` when syslog-ng is started or reloaded. If `fetch()` returns with an error, syslog-ng OSE calls the `close()` and `open()` methods before trying to fetch a new message.

If `open()` fails, it should return the False value. In this case, syslog-ng OSE retries it every `time-reopen()` seconds.

- `close()`

This method can be used to close connection towards the entities, from which the driver needs to fetch logs.

This method is called before `deinit()`. It is also called if `fetch()` returns with `LogFetcher.FETCH_ERROR`. In that case, syslog-ng will wait `time-reopen()` seconds before calling `open()` again.

### Example
The example below encapsulates a http response into a logmessage, that will be printed to the screen.
```
@version: 3.21

log {
    source { python-fetcher(class("MyFetcher") options("server" "127.0.0.1")  flags(no-parse)); };
    destination { file("/dev/stdout"); };
};

python {

from syslogng import LogFetcher
from syslogng import LogMessage
from http.client import HTTPConnection

class MyFetcher(LogFetcher):
    def init(self, options):
        self.url = options["server"]
        self.connection = None
        return True

    def open(self):
        self.connection = HTTPConnection(self.url)
        return True

    def close(self):
        self.connection.close()

    def fetch(self):
        self.connection.request("GET", "/log")
        response = self.connection.getresponse()
        # return LogFetcher.FETCH_ERROR,
        # return LogFetcher.FETCH_NOT_CONNECTED,
        # return LogFetcher.FETCH_TRY_AGAIN,
        # return LogFetcher.FETCH_NO_DATA,
        return LogFetcher.FETCH_SUCCESS, LogMessage(response.read())

    def request_exit(self):
        self.connection.close()
};
```

## Python Source
A Python Source implementation must be inherited from `syslogng.LogSource`. Messages can be posted using `LogSource::post_message()`
- `post_message(syslogng.LogMessage)`
This method sends a log message object to syslog-ng. It must be called from the main thread of the python process.

In case the source needs to be suspended after the current message, `post_message` will block until the source is woken up by syslog-ng. If application specific logic needs to be called to prepare such block, it can be done in the `suspend()` `wakeup()` methods.
Suspend can happen for example when flow-control is enabled (`flags(flow-control)` in the logpath), and a destination cannot send logs. In that case the log messages are collected in the buffer of a destination, but after a point, syslog-ng cannot handle more logs, and the sources need to be suspended. `suspend()` should prevent the source from posting new messages until `wakeup()` is called. If this rule is violated, messages will be dropped with an error message: `Incorrectly suspended source, dropping message`.

There are two mandatory methods: `run()` and `request_exit()`
- `run()`

This method can be used to implement an event loop or start a server framework/library. It is responsible for posting messages to syslog-ng. Currenty, `run()` stops permanently if an exception is propagated back to the C side. This might change in the future.

- `request_exit()`

This method is called before syslog-ng terminates or reloads. Any blocking call inside `run()` must be cancelled here. This method is called from a different thread than the python main thread.

Optional methods: `init()`, `deinit()`, `suspend()`, `wakeup()`.

- `init(options)`

This method is called during initializaton: when syslog-ng starts, or after syslog-ng reloads. If there were options provided in the configuration, they will be available in the sole parameter of `init()`.
The return value is `True`/`False`. If `False` is returned, syslog-ng will not start.

- `deinit()`

This method is called during deinitialization: when syslog-ng stops, or before syslog-ng reloads.

- `suspend()`

This method is called by syslog-ng when the source needs to be suspended: the message posting must be stopped temporarily.
This happens for example when flow-control is enabled (`flags(flow-control)` in the logpath), and a destination cannot send logs. In that case the log messages are collected in the buffer of a destination, but after a point, syslog-ng cannot handle more logs, and the sources need to be suspended.

- `wakeup()`

This method is called by syslog-ng when the source needs to be woken op: the message posting can continue. See `suspend()`.

### Example: generator source
In this example: the python source will a test message in every second.

```
@version: 3.21

log {
  source { python(class("PySource") options("freq" "1") flags(no-parse)); };
  destination { file(/dev/stdout); };
};

python {
from syslogng import LogSource
from syslogng import LogMessage
from threading import Event

class PySource(LogSource):
    def init(self, options):
        self.freq = int(options["freq"])
        self.wait = Event()
        return True

    def run(self):
        while True:
            self.post_message(LogMessage("hello world"))
            timeout = self.wait.wait(self.freq)
            if timeout:
                break

    def request_exit(self):
        self.wait.set()
};
```

### Example: eventloop
In this example, we will use python `AsyncIO` library to run an eventloop. Eventloop will schedule two timers periodically. Each timer posts a message to syslog-ng.

```
@version: 3.21

log {
  source { python(class("PySource") flags(no-parse)); };
  destination { file(/dev/stdout); };
};

python {
from syslogng import LogSource
from syslogng import LogMessage
from threading import Event
import asyncio

class PySource(LogSource):
    FREQ1 = 1
    FREQ2 = 2
    def init(self, options):
        self.eventloop = asyncio.new_event_loop()
        self.timer1 = None
        self.timer2 = None
        return True

    def sendMessage1(self):
        self.post_message(LogMessage("msg1"))
        self.timer1 = self.eventloop.call_later(self.FREQ1, self.sendMessage1)

    def sendMessage2(self):
        self.post_message(LogMessage("msg2"))
        self.timer2 = self.eventloop.call_later(self.FREQ2, self.sendMessage2)

    def run(self):
        self.timer1 = self.eventloop.call_later(self.FREQ1, self.sendMessage1)
        self.timer2 = self.eventloop.call_later(self.FREQ2, self.sendMessage2)
        self.eventloop.run_forever()

    def request_exit(self):
        self.timer1.cancel()
        self.timer2.cancel()
        self.eventloop.call_soon_threadsafe(self.eventloop.stop)
};
```
