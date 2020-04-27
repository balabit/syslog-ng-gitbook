
# Source Driver

This section will guide you through the process of creating a source driver plugin, by going through the files of `static-file`, a source driver that reads existing log messages from a text file.

### Example Config
```
log {
  source {
    example-static-file("/tmp/input.log");
  };
  destination {
    file("/tmp/output.log");
  };
};
```

### UML Diagram

![](https://i.imgur.com/alNhdDK.png)

### `static-file-parser.h`

```
#ifndef STATIC_FILE_PARSER_H
#define STATIC_FILE_PARSER_H

#include "cfg-parser.h"
#include "driver.h"

extern CfgParser static_file_parser;

CFG_PARSER_DECLARE_LEXER_BINDING(static_file_, LogDriver **)

#endif
```

### `static-file-parser.c`

```
#include "driver.h"
#include "cfg-parser.h"
#include "static-file-grammar.h"

extern int static_file_debug;

int static_file_parse(CfgLexer *lexer, LogDriver **instance, gpointer arg);
```

We add a keyword for declaring the use of our plugin.
```
static CfgLexerKeyword static_file_keywords[] =
{
  { "example_static_file", KW_STATIC_FILE },
  { NULL }
};


CfgParser static_file_parser =
{
#if ENABLE_DEBUG
  .debug_flag = &static_file_debug,
#endif
  .name = "static_file",
  .keywords = static_file_keywords,
  .parse = (gint (*)(CfgLexer *, gpointer *, gpointer)) static_file_parse,
  .cleanup = (void (*)(gpointer)) log_pipe_unref,
};

CFG_PARSER_IMPLEMENT_LEXER_BINDING(static_file_, LogDriver **)
```

### `static-file-grammar.ym`

```
%code top {
#include "static-file-parser.h"
}

%code {

#include "static-file.h"
#include "logthrsource/logthrsourcedrv.h"
#include "cfg-parser.h"
#include "static-file-grammar.h"
#include "syslog-names.h"
#include "messages.h"
#include "plugin.h"
#include "cfg-grammar.h"
#include "template/templates.h"

#include <string.h>

}

%name-prefix "static_file_"

/* Add additional parameters to the lex and parse functions */
%lex-param {CfgLexer *lexer}
%parse-param {CfgLexer *lexer}
%parse-param {LogDriver **instance}
%parse-param {gpointer arg}
```

The following line is a macro, not a comment, and must be included. It copies in the Bison declarations found in `lib/cfg-grammar.y`.
```
/* INCLUDE_DECLS */
```

Here is the token for our `"example_static_file"` keyword.
```
%token KW_STATIC_FILE
```

We declare the grammar rules as pointer types.
```
%type <ptr> source_static_file
%type <ptr> source_static_file_params

%%
```

The rule here says that we find a `static-file` declaration inside a source block.
```
start
  : LL_CONTEXT_SOURCE source_static_file  { YYACCEPT; }
  ;
```

This rule says that a `static-file` declaration is made up of the `static-file` keyword token next to parameters for `static-file` in parantheses.
```
source_static_file
  : KW_STATIC_FILE '(' source_static_file_params ')' { $$ = $3; }
  ;
```

This rule says that the parameters for `static-file` will always begin with a string. This string is the pathname of the static file. With this string, we can call our function to create a new `static-file` source driver. `instance` is used to return the new driver back to the caller. `configuration` is the `GlobalConfig` that represents the user's config file.

The midrule in this rule says that after the string for the pathname are options for the `static-file` driver.
```
source_static_file_params
  : string
    {
      last_driver = *instance = static_file_sd_new($1, configuration);
    }
  source_static_file_options
    {
      $$ = last_driver;
    }
  ;
```

This rule says that there can be any number of options (zero or more).
```
source_static_file_options
  : source_static_file_option source_static_file_options
  |
  ;
```

This rule contains all the possible `static-file` options. There aren't any options specific to `static-file`, so we only include `threaded_source_driver_option` and `threaded_fetcher_driver_option`, which are standard options to include for all threaded source drivers and threaded fetcher drivers, respectively (both of which `static-file` is). Implementing plugin-specific options and flags is covered in the parser section of this guide.
```
source_static_file_option
  : threaded_source_driver_option
  | threaded_fetcher_driver_option
  ;
```

The following line is also a macro. It copies in the Bison rules found in `lib/cfg-grammar.y`.
```
/* INCLUDE_RULES */

%%
```

### `static-file-reader.h`

This is the header file for our file reader. Its implementation can be ignored. It is just a simple file reader and does not interface with syslog-ng.
```
#ifndef STATIC_FILE_READER_H
#define STATIC_FILE_READER_H

#include <stdio.h>

#include "syslog-ng.h"

typedef struct _StaticFileReader
{
  FILE *file;
} StaticFileReader;

StaticFileReader *sfr_new(void);
gboolean sfr_open(StaticFileReader *self, gchar *pathname);
GString *sfr_nextline(StaticFileReader *self, gsize maxlen);
void sfr_close(StaticFileReader *self);
void sfr_free(StaticFileReader *self);

#endif
```

### `static-file.h`

There are different types of source driver classes that we can extend from, and therefore various ways of implementing a source driver. The one we will use is `LogThreadedFetcherDriver`. Its methods are:
* `connect`, which establishes a connection between the source driver and the actual source of the log messages. In this case the source is a static text file, and so establishing a connection means opening the file.
* `disconnect`, which severs the connection between the source driver and source. In this case it means closing the file.
* `fetch`, which is a method that is automatically called to get and return a new log message from the source. In this case it means to read a line from the file.

The class that `LogThreadedFetcherDriver` is a based on, `LogThreadedSoruceDriver`, allows for more control by giving access to an abstract method `run`, which allows for control over how and when the `LogMessage` are sent. And this class is in turn based on `LogSrcDriver`, which has a more complicated implementation process, since it takes away the abstractions that the threaded source drivers offer.

See [here](https://github.com/balabit/syslog-ng/pull/2247) for more information on threaded source drivers.
```
#ifndef STATIC_FILE_H
#define STATIC_FILE_H

#include "syslog-ng.h"
#include "driver.h"
#include "logthrsource/logthrfetcherdrv.h"
#include "static-file-reader.h"

#define SF_MAXLEN 1000

typedef struct _StaticFileSourceDriver
{
  LogThreadedFetcherDriver super;
  StaticFileReader *reader;
  gchar *pathname;
} StaticFileSourceDriver;

LogDriver *static_file_sd_new(gchar *pathname, GlobalConfig *cfg);

#endif
```

### `static-file-source.c`

This function is called from the grammar file. It creates and returns a new `static-file` source driver. It can be thought of as the constructor for `StaticFileSourceDriver`.
```
LogDriver *
static_file_sd_new(gchar *pathname, GlobalConfig *cfg)
{
  /* Allocate memory, zeroed so that we can check for uninitialized fields later on */
  StaticFileSourceDriver *self = g_new0(StaticFileSourceDriver, 1);
```

In general, `new` functions will call the `init_instance` function for the superclass of the object being created. What the `init_instance` function does is:
1. Call the `init_instance` function for the class one step up (so `init_instance` functions are kind of recursive).
2. Perform any necessary initial operations for the `init_instance` function's class.
3. Set any default methods for the `init_instance` function's class.

In this case, we are calling the `init_instance` function for `LogThreadedFetcherDriver` because it is the superclass of `StaticFileSourceDriver`. What it first does is call the `init_instance` function one class up, which is `log_threaded_source_driver_init_instance`. And of course that function will do the same thing and call the `init_instance` function another step up. This behaviour is like constructor chaining.

The inital operations this `init_instance` function performs are function calls related to the worker thread.

The methods this `init_instance` function sets defaults for are `init`, `deinit`, and `free_fn`. This means we can override the functions that we need, like `free`, since we have data specific to `StaticFileSourceDriver` that we need to free. But, we can use the defaults for methods where we don't need to do anything special, like `deinit`, since while the reader needs to close its file (which is handled in `close`), the driver itself has nothing it needs to deinitialise that is specific to `static-file`. The default method will deinitialise anything that needs to be deinitialised.

However, we notice that this `init_instance` function does not set a default for `fetch`, which makes sense, because there could not be a sensible default for that function. So, `init`, `deinit`, and `free_fn` are like virtual methods, while `fetch` is like an abstract method.
```
  log_threaded_fetcher_driver_init_instance(&self->super, cfg);

  /* Set the methods for LogThreadedFetcherDriver */
  self->super.connect = _open_file;
  self->super.disconnect = _close_file;
  self->super.fetch = _fetch_line;

  /* Set the methods for other superclasses */
  self->super.super.super.super.super.free_fn = _free;
  self->super.super.format_stats_instance = _format_stats_instance;

  /* Set the StaticFile specific fields */
  self->reader = sfr_new();
  self->pathname = g_strdup(pathname);

  return &self->super.super.super.super;
}

static gboolean
_open_file(LogThreadedFetcherDriver *s)
{
  StaticFileSourceDriver *self = (StaticFileSourceDriver *) s;
  return sfr_open(self->reader, self->pathname);
}
```

Here is our implementation of the `fetch` method. It's job is to get and return a new log message from the source each time it is called. The type of the return value is a `LogThreadedFetchResult`, which is just a `LogMessage` with a status code at the beginning. This can be one of three things:
* `THREADED_FETCH_SUCCESS`, to indicate a successful message fetch.
* `THREADED_FETCH_NOT_CONNECTED`, to indicate the connection to the source is no longer working.
* `THREADED_FETCH_ERROR`, to indicate an error has occured.
```
static LogThreadedFetchResult
_fetch_line(LogThreadedFetcherDriver *s)
{
  StaticFileSourceDriver *self = (StaticFileSourceDriver *) s;

  GString *line = sfr_nextline(self->reader, SF_MAXLEN);

  /* EOF */
  if (!line)
    {
      LogThreadedFetchResult result = { THREADED_FETCH_NOT_CONNECTED, NULL };
      return result;
    }
    
  /* Get rid of the \n at the end, since we assume the template will place another one */
  g_string_truncate(line, line->len-1);
```

We create an empty `LogMessage`, set its `${MESSAGE}` part to the string we got from the reader, and return it as a successful `LogThreadedFetchResult`.
```
  LogMessage *msg = log_msg_new_empty();
  log_msg_set_value(msg, LM_V_MESSAGE, line->str, line->len);
  LogThreadedFetchResult result = { THREADED_FETCH_SUCCESS, msg };
  return result;
}

static void
_close_file(LogThreadedFetcherDriver *s)
{
  StaticFileSourceDriver *self = (StaticFileSourceDriver *) s;
  sfr_close(self->reader);
}
```

This function will override the default `free` method. But notice that we are calling the default method at the end anyway. This is because we don't want to replace the default functionality (since it does useful things like freeing up the memory for the superclasses), we just want to add to it. This is a common thing to do when overriding virtual methods.
```
static void
_free(LogPipe *s)
{
  StaticFileSourceDriver *self = (StaticFileSourceDriver *) s;

  g_free(self->pathname);
  sfr_free(self->reader);

  log_threaded_fetcher_driver_free_method(s);
}

static const gchar *
_format_stats_instance(LogThreadedSourceDriver *s)
{
  StaticFileSourceDriver *self = (StaticFileSourceDriver *) s;
  static gchar persist_name[1024];

  if (s->super.super.super.persist_name)
    g_snprintf(persist_name, sizeof(persist_name), "static-file,%s", s->super.super.super.persist_name);
  else
    g_snprintf(persist_name, sizeof(persist_name), "static-file,%s", self->pathname);

  return persist_name;
}
```
