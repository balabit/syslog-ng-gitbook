# Simple Threaded C Destination

In order to implement a threaded C destination, you need to create a syslog-ng module and a plugin in it.
At the end of this section you're going to be ready to start syslog-ng with the following configuration:

```C
@version: 3.8
@include "scl.conf"

source s_local {
    system();
    internal();
};

destination d_dummy {
    dummy(filename("/tmp/test"));
};

log {
    source(s_local);
    destination(d_dummy);
};
```

### Creating a module
Make a new folder in syslog-ng's modules directory, for example: `dummy`, and create a file structure that is similar to the following.
```
modules/dummy
├── dummy-grammar.ym
├── dummy-parser.c
├── dummy-parser.h
├── dummy.c
├── dummy.h
└── Makefile.am
```

- The `dummy-grammar` and `dummy-parser` files will contain the configuration grammar. Parser codes are generated from these.
- `dummy` will implement the destination logic through interfaces.

When you are writing a destination, you should extend from one of these abstract classes: `LogThreadedDestDriver`, `LogDestDriver`.

This example shows an empty and very simple LogThreadedDestDriver (threaded destination driver) implementation.
In this case, we have a dedicated thread so it's allowed to use blocking operations.

### Dummy Destination

#### dummy.h
The destination header file only contains the initialization functions needed by the config parser.
- `dummy_dd_new`: constructs our destination
- `dummy_dd_set_*`: option setter functions for the parser

This example has only one dummy filename option.

```C
#ifndef DUMMY_H_INCLUDED
#define DUMMY_H_INCLUDED

#include "driver.h"

LogDriver *dummy_dd_new(GlobalConfig *cfg);

void dummy_dd_set_filename(LogDriver *d, const gchar *filename);

#endif
```

#### dummy.c

This is the implementation of the destination driver. It will be built as a shared or static library.
```C
#include "dummy.h"
#include "dummy-parser.h"

#include "plugin.h"
#include "messages.h"
#include "misc.h"
#include "stats/stats-registry.h"
#include "logqueue.h"
#include "driver.h"
#include "plugin-types.h"
#include "logthrdest/logthrdestdrv.h"


typedef struct
{
  LogThreadedDestDriver super;
  gchar *filename;
} DummyDriver;

/*
 * Configuration
 */

void
dummy_dd_set_filename(LogDriver *d, const gchar *filename)
{
  DummyDriver *self = (DummyDriver *)d;

  g_free(self->filename);
  self->filename = g_strdup(filename);
}

/*
 * Utilities
 */

static const gchar *
dummy_dd_format_stats_instance(LogThreadedDestDriver *d)
{
  DummyDriver *self = (DummyDriver *)d;
  static gchar persist_name[1024];

  g_snprintf(persist_name, sizeof(persist_name),
             "dummy,%s", self->filename);
  return persist_name;
}

static const gchar *
dummy_dd_format_persist_name(const LogPipe *d)
{
  DummyDriver *self = (DummyDriver *)d;
  static gchar persist_name[1024];

  if (d->persist_name)
    g_snprintf(persist_name, sizeof(persist_name), "dummy.%s", d->persist_name);
  else
    g_snprintf(persist_name, sizeof(persist_name), "dummy.%s", self->filename);

  return persist_name;
}

static gboolean
dummy_dd_connect(DummyDriver *self, gboolean reconnect)
{
  msg_debug("Dummy connection succeeded",
            evt_tag_str("driver", self->super.super.super.id), NULL);

  return TRUE;
}

static void
dummy_dd_disconnect(LogThreadedDestDriver *d)
{
  DummyDriver *self = (DummyDriver *)d;

  msg_debug("Dummy connection closed",
            evt_tag_str("driver", self->super.super.super.id), NULL);
}

/*
 * Worker thread
 */

static LogThreadedResult
dummy_worker_insert(LogThreadedDestDriver *d, LogMessage *msg)
{
  DummyDriver *self = (DummyDriver *)d;

  msg_debug("Dummy message sent",
            evt_tag_str("driver", self->super.super.super.id),
            evt_tag_str("filename", self->filename),
            NULL);

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

static void
dummy_worker_thread_init(LogThreadedDestDriver *d)
{
  DummyDriver *self = (DummyDriver *)d;

  msg_debug("Worker thread started",
            evt_tag_str("driver", self->super.super.super.id),
            NULL);

  dummy_dd_connect(self, FALSE);
}

static void
dummy_worker_thread_deinit(LogThreadedDestDriver *d)
{
  DummyDriver *self = (DummyDriver *)d;

  msg_debug("Worker thread stopped",
            evt_tag_str("driver", self->super.super.super.id),
            NULL);
}

/*
 * Main thread
 */

static gboolean
dummy_dd_init(LogPipe *d)
{
  DummyDriver *self = (DummyDriver *)d;
  GlobalConfig *cfg = log_pipe_get_config(d);

  if (!log_threaded_dest_driver_init_method(d))
    return FALSE;

  msg_verbose("Initializing Dummy destination",
              evt_tag_str("driver", self->super.super.super.id),
              evt_tag_str("filename", self->filename),
              NULL);

  return log_threaded_dest_driver_start_workers(&self->super);
}

static void
dummy_dd_free(LogPipe *d)
{
  DummyDriver *self = (DummyDriver *)d;

  g_free(self->filename);

  log_threaded_dest_driver_free(d);
}

/*
 * Plugin glue.
 */

LogDriver *
dummy_dd_new(GlobalConfig *cfg)
{
  DummyDriver *self = g_new0(DummyDriver, 1);

  log_threaded_dest_driver_init_instance(&self->super, cfg);
  self->super.super.super.super.init = dummy_dd_init;
  self->super.super.super.super.free_fn = dummy_dd_free;

  self->super.worker.thread_init = dummy_worker_thread_init;
  self->super.worker.thread_deinit = dummy_worker_thread_deinit;
  self->super.worker.disconnect = dummy_dd_disconnect;
  self->super.worker.insert = dummy_worker_insert;

  self->super.format_stats_instance = dummy_dd_format_stats_instance;
  self->super.super.super.super.generate_persist_name = dummy_dd_format_persist_name;
  //self->super.stats_source = SCS_DUMMY;

  return (LogDriver *)self;
}

extern CfgParser dummy_parser;

static Plugin dummy_plugin =
{
  .type = LL_CONTEXT_DESTINATION,
  .name = "dummy",
  .parser = &dummy_parser,
};

gboolean
dummy_module_init(PluginContext *context, CfgArgs *args)
{
  plugin_register(context, &dummy_plugin, 1);

  return TRUE;
}

const ModuleInfo module_info =
{
  .canonical_name = "dummy",
  .version = SYSLOG_NG_VERSION,
  .description = "This is a dummy destination for syslog-ng.",
  .core_revision = SYSLOG_NG_SOURCE_REVISION,
  .plugins = &dummy_plugin,
  .plugins_len = 1,
};
```

This unit can be separated into 5 parts:

1. configuration functions (setters)
2. utility functions
3. functions running in separate thread
4. functions running in the main thread
5. plugin-construction declarations

Functions from category 2-4 are implementations of the LogThreadedDestDriver's virtual methods.
In `dummy_dd_new`, we pass these function pointers to the base classes.

Our example overrides these 6 virtual methods:

- `init (dummy_dd_init)`: destination constructor
- `free_fn (dummy_dd_free)`: destination destructor
- `thread_init (dummy_worker_thread_init)`: worker thread initialization
- `thread_deinit (dummy_worker_thread_deinit)`: worker thread deinitialization
- `disconnect (dummy_dd_disconnect)`: destination disconnects (on error or drop)

The most important method is the `insert (dummy_worker_insert)`, where you can format the received message and send to an actual destination.

### dummy-parser

In this unit, we declare the keywords used in the syslog-ng.conf file and call the lexical analyzer.

#### dummy-parser.h

```C
#ifndef DUMMY_PARSER_H_INCLUDED
#define DUMMY_PARSER_H_INCLUDED

#include "cfg-parser.h"
#include "cfg-lexer.h"
#include "dummy.h"

extern CfgParser dummy_parser;

CFG_PARSER_DECLARE_LEXER_BINDING(dummy_, LogDriver **)

#endif
```

#### dummy-parser.c

```C
#include "dummy.h"
#include "cfg-parser.h"
#include "dummy-grammar.h" // generated by lexer

extern int dummy_debug;
int dummy_parse(CfgLexer *lexer, LogDriver **instance, gpointer arg);

static CfgLexerKeyword dummy_keywords[] = {
  { "dummy", KW_DUMMY },
  { "filename", KW_FILENAME },
  { NULL }
};

CfgParser dummy_parser =
{
#if SYSLOG_NG_ENABLE_DEBUG
  .debug_flag = &dummy_debug,
#endif
  .name = "dummy",
  .keywords = dummy_keywords,
  .parse = (int (*)(CfgLexer *lexer, gpointer *instance, gpointer)) dummy_parse,
  .cleanup = (void (*)(gpointer)) log_pipe_unref,
};

CFG_PARSER_IMPLEMENT_LEXER_BINDING(dummy_, LogDriver **)
```

### dummy-grammar

The dummy-grammar.ym file writes down the syntax of the configuration of our destination. It's written in yacc format. The bison parser generator creates parser code from this grammar.

#### dummy-grammar.ym

```C
%code requires {

#include "dummy-parser.h"

}

%code {

#include "cfg-grammar.h"
#include "plugin.h"
}

%name-prefix "dummy_"
%lex-param {CfgLexer *lexer}
%parse-param {CfgLexer *lexer}
%parse-param {LogDriver **instance}
%parse-param {gpointer arg}

/* INCLUDE_DECLS */

%token KW_DUMMY
%token KW_FILENAME

%%

start
        : LL_CONTEXT_DESTINATION KW_DUMMY
          {
            last_driver = *instance = dummy_dd_new(configuration);
          }
          '(' dummy_option ')' { YYACCEPT; }
;

dummy_options
        : dummy_option dummy_options
        |
        ;

dummy_option
        : KW_FILENAME '(' string ')'
          {
            dummy_dd_set_filename(last_driver, $3);
            free($3);
          }
        | threaded_dest_driver_option
;

/* INCLUDE_RULES */

%%

```
### Makefile

You should create a `Makefile.am` automake file to build the destination module.

```Makefile
module_LTLIBRARIES          +=          \
    modules/dummy/libdummy.la

modules_dummy_libdummy_la_CFLAGS    =   \
    -I$(top_srcdir)/modules/dummy       \
    -I$(top_builddir)/modules/dummy
modules_dummy_libdummy_la_SOURCES   =   \
    modules/dummy/dummy-grammar.y       \
    modules/dummy/dummy.c               \
    modules/dummy/dummy.h               \
    modules/dummy/dummy-parser.c        \
    modules/dummy/dummy-parser.h
modules_dummy_libdummy_la_LIBADD    =   \
    $(MODULE_DEPS_LIBS)
modules_dummy_libdummy_la_LDFLAGS   =   \
    $(MODULE_LDFLAGS)
modules_dummy_libdummy_la_DEPENDENCIES  =   \
    $(MODULE_DEPS_LIBS)

modules/dummy modules/dummy/ mod-dummy: \
    modules/dummy/libdummy.la

BUILT_SOURCES               +=          \
    modules/dummy/dummy-grammar.y       \
    modules/dummy/dummy-grammar.c       \
    modules/dummy/dummy-grammar.h
EXTRA_DIST                  +=          \
    modules/dummy/dummy-grammar.ym

.PHONY: modules/dummy/ mod-dummy
```

Finally, include the dummy module's Makefile into `modules/Makefile.am` and add the module's name to the SYSLOG_NG_MODULES variable.

```Makefile
...

include modules/native/Makefile.am
include modules/dummy/Makefile.am

SYSLOG_NG_MODULES = \
  mod-afsocket mod-afstreams mod-affile mod-afprog \
  mod-usertty mod-amqp mod-mongodb mod-smtp mod-json \
  mod-syslogformat mod-linux-kmsg mod-pacctformat \
  mod-confgen mod-system-source mod-csvparser mod-dbparser \
  mod-basicfuncs mod-cryptofuncs mod-geoip mod-afstomp \
  mod-redis mod-pseudofile mod-graphite mod-riemann \
  mod-python mod-java mod-java-modules mod-kvformat mod-date \
  mod-native mod-dummy

modules modules/: ${SYSLOG_NG_MODULES}

...
```
