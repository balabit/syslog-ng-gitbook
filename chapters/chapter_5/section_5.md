# Simple Threaded C Destination

In this guide, we will implement a threaded destination driver in C, called `example-destination`.

It will have one optional parameter: `filename`, with `"output.txt"` as default value.

Config example:
```C
@version: 3.28

source s_local {
    system();
    internal();
};

log {

  source(s_local);
  destination { example-destination(filename("output.txt")); };
};
```

`example-destination` will write data to `filename`. The data will contain the thread id of the thread that writes to the file, and the original message, in the following format:

```
thread_id=140495535482624 message=-- Generated message. --
```

In order to implement a threaded C destination, you need to create a syslog-ng module and a plugin in it.

You can find `example-destination` in the [repository](https://github.com/syslog-ng/syslog-ng/tree/master/modules/examples/destinations/example_destination). There are a few differences to the shipped version, compared to the code that we walk through here:
- The shipped module is not under `modules/example_destination`, but under `modules/examples/destinations/example_destinations`, together with the other examples.
- It is not a module on it's own, but it is part of a larger `libexamples` module.
- It is built as static into `libexamples`. The destination in this guide is put into it's own dynamic library.
- The `ModuleInfo` of the shipped version is set in a different location: in the plugin list of `libexamples`.

**WARNING**: If you try and follow this guide, there will be a collision with the shipped version of `example-destination` and your version. To avoid that, you either need to choose another name, or disable the shipped `example-destination` module.

To disable the shipped version, the simplest solution is to remove the entire examples module from the build system.
- autotools

Remove `include modules/examples/Makefile.am` from `modules/Makefile.am`.

- cmake

Remove `add_subdirectory(examples)`

### Creating a module skeleton

You can use a development script that prepares a skeleton code for the destination:
```
$ dev-utils/plugin_skeleton_creator/create_plugin.sh -n example_destination -k example_destination -t LL_CONTEXT_DESTINATION
```

The command above will create the following files.
```
modules/example_destination
├── CMakeLists.txt
├── example_destination-grammar.ym
├── example_destination-parser.c
├── example_destination-parser.h
├── example_destination-plugin.c
└── Makefile.am
```

The next step is make the build system notice the new module. Syslog-ng maintains two build systems in parallel: autotools and cmake.

- autotools

Add `include modules/example_destination/Makefile.am` for `modules/Makefile.am`, and add `mod-example_destination` to the `SYSLOG_NG_MODULES` variable.

- cmake

Add `add_subdirectory(example_destination)` for `modules/CMakeLists.txt`.

The `example_destination-grammar` and `example_destination-parser` files will contain the configuration grammar. Parser codes are generated from these.

### Example Destination

A threaded destination consists of a driver, and one or more workers. In this example, we will have only one worker. If you need more workers, all you need to do is to call `log_threaded_dest_driver_set_num_workers` similarly to other modules in the source code. Threaded destination driver has one worker by default.

When you are writing a destination, you should extend these abstract classes: `LogThreadedDestDriver`, `LogThreadedDestWorker`.

Workers use dedicated thread instead of the main thread (hence the name: threaded destination). So it's allowed to use blocking operations.

Create these new files:
- `example_destination.h`
- `example_destination.c`
- `example_destination_worker.h`
- `example_destination_worker.c`

These files needed to be added to the build system too.

- autotools

Add these files to `modules_example_destination_libexample_destination_la_SOURCES` in `modules/example_destination/Makefile.am`

- cmake

Add these files to `example_destination_SOURCES` in `modules/example_destination/CMakeLists.txt`.

#### example_destination.h
The destination header file only contains the initialization functions needed by the config parser.
- `example_destination_dd_new`: constructs the destination
- `example_destination_dd_set_*`: option setter functions for the parser

```C
#ifndef EXAMPLE_DESTINATION_H_INCLUDED
#define EXAMPLE_DESTINATION_H_INCLUDED

#include "driver.h"
#include "logthrdest/logthrdestdrv.h"

typedef struct
{
  LogThreadedDestDriver super;
  GString *filename;
} ExampleDestinationDriver;

LogDriver *example_destination_dd_new(GlobalConfig *cfg);

void example_destination_dd_set_filename(LogDriver *d, const gchar *filename);

#endif
```

#### example_destination.c

This is the implementation of the destination driver. It will be built as a shared library.

```C
#include "example_destination.h"
#include "example_destination_worker.h"
#include "example_destination-parser.h"

#include "plugin.h"
#include "messages.h"
#include "misc.h"
#include "stats/stats-registry.h"
#include "logqueue.h"
#include "driver.h"
#include "plugin-types.h"
#include "logthrdest/logthrdestdrv.h"


/*
 * Configuration
 */

void
example_destination_dd_set_filename(LogDriver *d, const gchar *filename)
{
  ExampleDestinationDriver *self = (ExampleDestinationDriver *)d;

  g_string_assign(self->filename, filename);
}

/*
 * Utilities
 */

static const gchar *
_format_stats_instance(LogThreadedDestDriver *d)
{
  ExampleDestinationDriver *self = (ExampleDestinationDriver *)d;
  static gchar persist_name[1024];

  g_snprintf(persist_name, sizeof(persist_name),
             "example-destination,%s", self->filename->str);
  return persist_name;
}

static const gchar *
_format_persist_name(const LogPipe *d)
{
  ExampleDestinationDriver *self = (ExampleDestinationDriver *)d;
  static gchar persist_name[1024];

  if (d->persist_name)
    g_snprintf(persist_name, sizeof(persist_name), "example-destination.%s", d->persist_name);
  else
    g_snprintf(persist_name, sizeof(persist_name), "example-destination.%s", self->filename->str);

  return persist_name;
}

static gboolean
_dd_init(LogPipe *d)
{
  ExampleDestinationDriver *self = (ExampleDestinationDriver *)d;

  if (!log_threaded_dest_driver_init_method(d))
    return FALSE;

  if (!self->filename->len)
    g_string_assign(self->filename, "/tmp/example-destination-output.txt");

  return TRUE;
}

gboolean
_dd_deinit(LogPipe *s)
{
  /*
     If you created resources during init,
     you need to destroy them here.
  */

  return log_threaded_dest_driver_deinit_method(s);
}

static void
_dd_free(LogPipe *d)
{
  ExampleDestinationDriver *self = (ExampleDestinationDriver *)d;

  g_string_free(self->filename, TRUE);

  log_threaded_dest_driver_free(d);
}

LogDriver *
example_destination_dd_new(GlobalConfig *cfg)
{
  ExampleDestinationDriver *self = g_new0(ExampleDestinationDriver, 1);
  self->filename = g_string_new("");

  log_threaded_dest_driver_init_instance(&self->super, cfg);
  self->super.super.super.super.init = _dd_init;
  self->super.super.super.super.deinit = _dd_deinit;
  self->super.super.super.super.free_fn = _dd_free;

  self->super.format_stats_instance = _format_stats_instance;
  self->super.super.super.super.generate_persist_name = _format_persist_name;
  self->super.stats_source = stats_register_type("example-destination");
  self->super.worker.construct = example_destination_dw_new;

  return (LogDriver *)self;
}
```

Our example overrides these virtual methods:

- `new (example_destination_dd_new)`: driver constructor.
- `free_fn (_dd_free)`: driver destructor.
- `init (_dd_init)`: It is called after startup, and after each reload. You can set default values here. It is important to note that the init method may be called multiple times for the same driver. In case of a failed reload (for example syntax error in config), syslog-ng will resume using the same driver instances instead of creating new ones, after calling their init method again.
- `deinit (_dd_deinit)`: It is called before shutdown, and before each reload. If you created resources during `init`, then you need to free them here.
- `format_stats_instance (_format_stats_instance)`: this specifies how this driver is represented with `syslog-ng-ctl stats` or `syslog-ng-ctl query get "*"`.
- `generate_persist_name (_generate_persist_name)`: this specifies the persist key of the driver in the persist file. This name is used when syslog-ng attaches a disk queue for a driver, for example.
- `construct (example_destination_dw_new)`: constructor for the worker. It is implemented in `example_destination_worker.c`.

#### example_destination_worker.h

```C
#ifndef EXAMPLE_DESTINATION_WORKER_H_INCLUDED
#define EXAMPLE_DESTINATION_WORKER_H_INCLUDED 1

#include "logthrdest/logthrdestdrv.h"
#include "thread-utils.h"


typedef struct _ExampleDestinationWorker
{
  LogThreadedDestWorker super;
  FILE *file;
  ThreadId thread_id;
} ExampleDestinationWorker;

LogThreadedDestWorker *example_destination_dw_new(LogThreadedDestDriver *o, gint worker_index);

#endif
```

#### example_destination_worker.c

This is the implementation of the worker.


```C
#include "example_destination_worker.h"
#include "example_destination.h"
#include "thread-utils.h"

#include <stdio.h>

static LogThreadedResult
_dw_insert(LogThreadedDestWorker *s, LogMessage *msg)
{
  ExampleDestinationWorker *self = (ExampleDestinationWorker *)s;

  GString *string_to_write = g_string_new("");
  g_string_printf(string_to_write, "thread_id=%lu message=%s\n",
                  self->thread_id, log_msg_get_value(msg, LM_V_MESSAGE, NULL));

  size_t retval = fwrite(string_to_write->str, 1, string_to_write->len, self->file);
  if (retval != string_to_write->len)
    {
      msg_error("Error while reading file");
      return LTR_NOT_CONNECTED;
    }

  if (fflush(self->file) != 0)
    {
      msg_error("Error while flushing file");
      return LTR_NOT_CONNECTED;
    }

  g_string_free(string_to_write, TRUE);

  return LTR_SUCCESS;
  /*
   * LTR_DROP,
   * LTR_ERROR,
   * LTR_SUCCESS,
   * LTR_QUEUED,
   * LTR_NOT_CONNECTED,
   * LTR_RETRY,
  */
}

static gboolean
_connect(LogThreadedDestWorker *s)
{
  ExampleDestinationWorker *self = (ExampleDestinationWorker *)s;
  ExampleDestinationDriver *owner = (ExampleDestinationDriver *) s->owner;

  self->file = fopen(owner->filename->str, "a");
  if (!self->file)
    {
      msg_error("Could not open file", evt_tag_error("error"));
      return FALSE;
    }

  return TRUE;
}

static void
_disconnect(LogThreadedDestWorker *s)
{
  ExampleDestinationWorker *self = (ExampleDestinationWorker *)s;

  fclose(self->file);
}

static gboolean
_thread_init(LogThreadedDestWorker *s)
{
  ExampleDestinationWorker *self = (ExampleDestinationWorker *)s;

  /*
    You can create thread specific resources here. In this example, we
    store the thread id.
  */
  self->thread_id = get_thread_id();

  return log_threaded_dest_worker_init_method(s);
}

static void
_thread_deinit(LogThreadedDestWorker *s)
{
  /*
    If you created resources during _thread_init,
    you need to free them here
  */

  log_threaded_dest_worker_deinit_method(s);
}

static void
_dw_free(LogThreadedDestWorker *s)
{
  /*
    If you created resources during new,
    you need to free them here.
  */

  log_threaded_dest_worker_free_method(s);
}

LogThreadedDestWorker *
example_destination_dw_new(LogThreadedDestDriver *o, gint worker_index)
{
  ExampleDestinationWorker *self = g_new0(ExampleDestinationWorker, 1);

  log_threaded_dest_worker_init_instance(&self->super, o, worker_index);
  self->super.thread_init = _thread_init;
  self->super.thread_deinit = _thread_deinit;
  self->super.insert = _dw_insert;
  self->super.free_fn = _dw_free;
  self->super.connect = _connect;
  self->super.disconnect = _disconnect;

  return &self->super;
}
```

Our example overrides these virtual methods:
- `thread_init (_thread_init)`: if you need to initialize thread specific resources, you can do them here. We are saving the thread id in this example. Non-thread specific resources may be created in the constructor (`example_destination_dw_new`).
- `thread_deinit (_thread_deinit)`: if you created resources during `thread_init`, you need to deallocate them here.
- `free_fn (_dw_free)` destructor for resources created in `example_destination_dw_new`.
- `insert (_dw_insert)`: It formats the received message and sends to an actual destination.
- `connect (_dw_connect)`: This is called after `thread_init`, before the first `insert`, and each time you signal error during insert (returning `LTR_ERROR`, `LTR_DROP` or `LTR_NOT_CONNECTED`). You can open files or establish connections here.
- `disconnect (_dw_disconnect)`: This is called before deinit, or when you signal broken connection from insert. You can close files or sockets here.

### grammar keywords

`example_destination-parser.c` contains a list of available keywords that can be referred in the grammar. A keyword is an integer with a string representation. The integer is defined in `example_destination-grammar.ym`: see the example below. The string representation is defined in `example_destination-grammar.c`.

The example destination module will support two keywords: `example_destination` and `filename`. You need to replace `example_destination-keywords` in `example_destination-parser.c` with:

```
static CfgLexerKeyword example_destination_keywords[] =
{
  { "example_destination", KW_EXAMPLE_DESTINATION },
  { "filename", KW_FILENAME },
  { NULL }
};
```

### grammar rules

The example_destination-grammar.ym file writes down the syntax of the configuration of our destination. It's written in yacc format. The bison parser generator creates parser code from this grammar.

#### example_destination-grammar.ym

```C
%code requires {

#include "example_destination-parser.h"

}

%code {

#include "example_destination.h"

#include "cfg-grammar.h"
#include "plugin.h"
}

%name-prefix "example_destination_"
%lex-param {CfgLexer *lexer}
%parse-param {CfgLexer *lexer}
%parse-param {LogDriver **instance}
%parse-param {gpointer arg}

/* INCLUDE_DECLS */

%token KW_EXAMPLE_DESTINATION
%token KW_FILENAME

%%

start
        : LL_CONTEXT_DESTINATION KW_EXAMPLE_DESTINATION
          {
            last_driver = *instance = example_destination_dd_new(configuration);
          }
          '(' example_destination_options ')' { YYACCEPT; }
;

example_destination_options
        : example_destination_option example_destination_options
        |
        ;

example_destination_option
        : KW_FILENAME '(' string ')'
          {
            example_destination_dd_set_filename(last_driver, $3);
            free($3);
          }
        | threaded_dest_driver_option
;

/* INCLUDE_RULES */

%%
```
