# Parser

This section will guide you through the process of creating a parser plugin, by going through the files of `ordered-parser`, which parses an ordered list by creating macros for each item in the list.

For example:
`A) Apple B) Banana C) Cherry -> ${A}="Apple", ${B}="Banana, ${C}="Cherry"`

This parser supports an option `suffix`, which lets the user choose what suffix their ordered lists use (`A) B) C)` vs. `A: B: C:`).

This parser also supports the option `prefix`, which allows the user to add a prefix before the generated macro names (so you could have `${orderedparser.A}` for example). This is a standard option for parsers. It is useful for avoiding macro collisions.

This parser also supports two flags, `letters` and `numbers`, which lets the user choose what symbols their ordered lists use (`A) B) C)` vs. `1) 2) 3)`).

### Example Config

```
source s_file {
  file("/tmp/input.log");
};

parser ordered {
  example_ordered_parser(flags(numbers));
};

template t_sqr {
  template("$(* $1 $1), $(* $2 $2), $(* $3 $3)\n");
};

destination d_file {
  file("/tmp/output.log" template(t_sqr));
};

log {
  source(s_file);
  parser(ordered);
  destination(d_file);
};
```

### UML Diagram

![](https://i.imgur.com/vhVizEX.png)

### `ordered-parser-parser.h`

```
#ifndef ORDERED_PARSER_PARSER_INCLUDED
#define ORDERED_PARSER_PARSER_INCLUDED

#include "cfg-parser.h"
#include "parser/parser-expr.h"

extern CfgParser ordered_parser_parser;

CFG_PARSER_DECLARE_LEXER_BINDING(ordered_parser_, LogParser **)

#endif
```

### `ordered-parser-parser.c`

```
#include "ordered-parser.h"
#include "cfg-parser.h"
#include "ordered-parser-grammar.h"

extern int ordered_parser_debug;

int ordered_parser_parse(CfgLexer *lexer, LogParser **instance, gpointer arg);
```

Here we have the keyword for the plugin itself, but we also add an additional keyword for the suffix and prefix options.
```
static CfgLexerKeyword ordered_parser_keywords[] =
{
  { "example_ordered_parser", KW_ORDERED_PARSER },
  { "suffix",                 KW_SUFFIX },
  { "prefix",                 KW_PREFIX },
  { NULL }
};

CfgParser ordered_parser_parser =
{
#if SYSLOG_NG_ENABLE_DEBUG
  .debug_flag = &ordered_parser_debug,
#endif
  .name = "ordered-parser",
  .keywords = ordered_parser_keywords,
  .parse = (gint (*)(CfgLexer *, gpointer *, gpointer)) ordered_parser_parse,
  .cleanup = (void (*)(gpointer)) log_pipe_unref,
};

CFG_PARSER_IMPLEMENT_LEXER_BINDING(ordered_parser_, LogParser **)
```

### `ordered-parser-grammar.ym`

```
%code top {
#include "ordered-parser-parser.h"
}

%code {
#include "ordered-parser.h"
#include "cfg-parser.h"
#include "ordered-parser-grammar.h"
#include "syslog-names.h"
#include "messages.h"
#include "cfg-grammar.h"
}

%name-prefix "ordered_parser_"

%lex-param   {CfgLexer *lexer}
%parse-param {CfgLexer *lexer}
%parse-param {LogParser **instance}
%parse-param {gpointer arg}

/* INCLUDE_DECLS */

%token  KW_ORDERED_PARSER
%token  KW_SUFFIX
%token  KW_PREFIX

%type <ptr> parser_expr_ordered

%%

start
    : LL_CONTEXT_PARSER parser_expr_ordered { YYACCEPT; }
    ;

parser_expr_ordered
    : KW_ORDERED_PARSER '('
      {
        last_parser = *instance = ordered_parser_new(configuration);
      }
      parser_ordered_opts ')'
      {
        $$ = last_parser;
      }
    ;

parser_ordered_opts
    : parser_ordered_opt parser_ordered_opts
    |
    ;
```

Here we add an option for flags (which are handled in the next block).

Since ordered-parser supports the `suffix` option, we need to implement that too. We first make two calls to the `CHECK_ERROR` macro, to make sure the input is a valid suffix. Then we call our setter function.

For our `prefix` option, we just need to call the setter function.

Finally, we add `parser_opt`, which is a standard option to include for parsers.
```
parser_ordered_opt
    : KW_FLAGS  '(' parser_ordered_flags ')'
    | KW_SUFFX '(' string ')'
      {
        CHECK_ERROR((strlen($3)==1), @3, "Suffix must be a single character");
        CHECK_ERROR((ordered_parser_suffix_valid($3[0])), @3, "Suffix character unsupported");
        ordered_parser_set_suffix(last_parser, $3[0]);
        free($3);
      }
    | KW_PREFIX '(' string ')'
      {
        ordered_parser_set_prefix(last_parser, $3);
        free($3);
      }
    | parser_opt
    ;
```

Ordered-parser supports two flags, so we implement the flag option here by calling our flag processing function.
```
parser_ordered_flags
    : string parser_ordered_flags
      {
        CHECK_ERROR(ordered_parser_process_flag(last_parser, $1), @1, "Unknown flag"); free($1);
      }
    |
    ;

/* INCLUDE_RULES */

%%
```

### `ordered-parser.h`

```
#ifndef ORDERED_PARSER_H_INCLUDED
#define ORDERED_PARSER_H_INCLUDED

#include "parser/parser-expr.h"
```

Parser classes extend `LogParser`, which has an abstract method `process`. `process` is where a parser's main functionality is implemented; it is the function that does the parsing.
```
typedef struct _OrderedParser
{
  LogParser super;
  gchar suffix;
  gchar *prefix;
  gsize prefix_len;
  guint32 flags;
} OrderedParser;

LogParser *ordered_parser_new(GlobalConfig *cfg);
gboolean ordered_parser_process_flag(LogParser *s, const gchar *flag);
gboolean ordered_parser_suffix_valid(gchar suffix);
void ordered_parser_set_suffix(LogParser *s, gchar suffix);
void ordered_parser_set_prefix(LogParser *s, gchar *prefix);

#endif
```

### `ordered-parser.c`

```
#include "ordered-parser.h"
#include "scanner/kv-scanner/kv-scanner.h"
#include "scratch-buffers.h"

LogParser *
ordered_parser_new(GlobalConfig *cfg)
{
  OrderedParser *self = g_new0(OrderedParser, 1);

  /* Standard init method for parsers */
  log_parser_init_instance(&self->super, cfg);

  /* Set methods */
  self->super.process = _process;
  self->super.super.clone = _clone;
  self->super.super.free_fn = _free;

  /* Set default options */
  self->suffix = ')';
  self->flags = 0x0000;

  return &self->super;
}
```
The next three blocks here deal with flag handling. Note that this plugin does not actually make use of the flags; they are just here for the purpose of this guide. But the flags field is just a standard bit field, so there is nothing special about using it.

First we define constants for each flag, assigning the `letters` flag to the first bit and `numbers` the second.
```
enum
{
  OPF_LETTERS = 0x0001,
  OPF_NUMBERS = 0x0002,
};
```

We create an array of `CfgFlagHandler` objects—one for each flag. With these we will be able to use the `cfg_process_flag` method, which will take care of the bit manipulation for us. The fields of `CfgFlagHandler` are as follows:

1. The name of the flag, which is what the user would type into their config file to use the flag.
2. The operation type, or what operation should be performed when the flag is used. This is either `CFH_SET`, which means to set (one) the bit, or `CFH_CLEAR`, which means to clear (zero) the bit.
4. The location of the `flags` field relative to the parser. This is needed because only the parser is passed into the `cfg_process_flag`, function so it needs to know where to find `flags`.
5. The constant value for the flag; the location of the bit to manipulate.
```
CfgFlagHandler ordered_parser_flag_handlers[] =
{
    { "letters", CFH_SET, offsetof(OrderedParser, flags), OPF_LETTERS},
    { "numbers", CFH_SET, offsetof(OrderedParser, flags), OPF_NUMBERS},
    { NULL },
};
```

This is the function called from our grammar file to set the flags. Because we have the flag handlers, we can use `cfg_process_flag` to do all the actual flag setting.
```
gboolean
ordered_parser_process_flag(LogParser *s, const gchar *flag)
{
  OrderedParser *self = (OrderedParser *) s;

  cfg_process_flag(ordered_parser_flag_handlers, self, flag);
}

gboolean
ordered_parser_suffix_valid(gchar suffix)
{
  return (suffix != ' '  && suffix != '\'' && suffix != '\"' );
}

void
ordered_parser_set_suffix(LogParser *s, gchar suffix)
{
  OrderedParser *self = (OrderedParser *) s;
  self->suffix = suffix;
}

void
ordered_parser_set_prefix(LogParser *s, gchar *prefix)
{
  OrderedParser *self = (OrderedParser *) s;

  /* prefix_len is needed due to the way the prefix+macro name is generated */

  g_free(self->prefix);
  if (prefix)
    {
      self->prefix = g_strdup(prefix);
      self->prefix_len = strlen(prefix);
    }
  else
    {
      self->prefix = NULL;
      self->prefix_len = 0;
    }
}

static char *
_format_input(const gchar *input, gchar suffix)
{
  /*
   * Prepare input for scanning; specific to ordered-parser.
   * Can be ignored.
   */
}
```

This function is called to get the macro name with any formatting necessary.
```
static const gchar *
_get_formatted_key(OrderedParser *self, const gchar *key, GString *formatted_key)
{
  if (!self->prefix)
    return key;
  return _get_formatted_key_with_prefix(self, key, formatted_key);
}
```

This function prepends the prefix to the macro name.
```
static const gchar *
_get_formatted_key_with_prefix(OrderedParser *self, const gchar *key, GString *formatted_key)
{
  if (formatted_key->len > 0)
    g_string_truncate(formatted_key, self->prefix_len);
  else
    g_string_assign(formatted_key, self->prefix);
  g_string_append(formatted_key, key);
  return formatted_key->str;
}
```

Here is the implementation of the `process` function for `ordered-parser`. `process` is called when a message needs to be parsed. The function takes in a string `input`, which is the message to parse, and returns the parsed `LogMessage` through `pmsg`. To parse the input means to add the appropriate key-value pairs to the returned `LogMessage`; these result in macros the user can use.

To actually extract the correct keys and values from the input string, we need to use a scanner, which will parse the text of `input` to give us the appropriate key-value pairs. Then, this function can just add these key-value pairs into `pmsg`. Normally we would need to write a scanner from scratch, but since the functionality of ordered-parser is essentially a subset of the functionality of kv-parser, we will use the kv-parser's scanner, `KVScanner`. Scanners can be found in `lib/scanner/`.

It is important to note that parsers do not require the use of a scanner (the date parser, for example, does not use one). However, scanners are often used.
```
static gboolean
_process(LogParser *s, LogMessage **pmsg, const LogPathOptions *path_options,
         const gchar *input, gsize input_len)
{
  OrderedParser *self = (OrderedParser *) s;

  KVScanner kv_scanner;

  /* Initialize scanner by passing in value and pair separators */
  kv_scanner_init(&kv_scanner, self->suffix, " ", FALSE);
  
  /* For efficiency reasons a "scratch buffer" is used to hold the macro name */
  GString *formatted_key = scratch_buffers_alloc();

  /* Delete spaces after suffix and pass input to KVScanner */
  gchar *formatted_input = _format_input(input, self->suffix);
  kv_scanner_input(&kv_scanner, formatted_input);

  /* Prepare to write macros to LogMessage */
  log_msg_make_writable(pmsg, path_options);
  msg_trace("ordered-parser message processing started",
            evt_tag_str ("input", input),
            evt_tag_str ("prefix", self->prefix),
            evt_tag_printf("msg", "%p", *pmsg));
```

Next we have the main parsing loop. It tells the scanner to move on to the next element, and then get the key and value of that element. After, we add the key-value pair to `pmsg` by calling the `log_msg_set_value_by_name` function.
```
  while (kv_scanner_scan_next(&kv_scanner))
    {
      const gchar *current_key = kv_scanner_get_current_key(&kv_scanner);
      const gchar *current_value = kv_scanner_get_current_value(&kv_scanner);
      log_msg_set_value_by_name(*pmsg,
                                _get_formatted_key(self, current_key, formatted_key),
                                current_value, -1);
    }
    
  kv_scanner_deinit(&kv_scanner);
  g_free(formatted_input);

  return TRUE;
}
```

Finally we need to implement the clone function, which is called when the same parser is used in multiple log paths.
```
static LogPipe *
_clone(LogPipe *s)
{
  OrderedParser *self = (OrderedParser *) s;

  OrderedParser *cloned;
  cloned = (OrderedParser *) ordered_parser_new(log_pipe_get_config(s));

  return ordered_parser_clone_method(cloned, self);
}

LogPipe *
ordered_parser_clone_method(OrderedParser *dst, OrderedParser *src)
{
  ordered_parser_set_suffix(&dst->super, src->suffix);
  ordered_parser_set_prefix(&dst->super, src->prefix);
  dst->flags = src->flags;

  return &dst->super.super;
}


static void
_free(LogPipe *s)
{
  OrderedParser *self = (OrderedParser *) s;

  g_free(self->prefix);
}
```

### `test_ordered_parser.c`

```
#include "ordered-parser.h"
#include "apphook.h"
#include "msg_parse_lib.h"
#include "scratch-buffers.h"

#include <criterion/criterion.h>
```

This global variable is declared in order to use the same `OrderedParser` throughout each stage of the testing process (setup, unit testing, teardown). Note, however, that globals are not actually shared between individual tests.
```
LogParser *ordered_parser;
```

This function uses `ordered_parser` to parse a given ordered list; the given list is meant to represent the `${MESSAGE}` part of a syslog message. We will use this function within each unit test.
```
static LogMessage *
parse_ordered_list_into_log_message(const gchar *ordered_list)
{
  LogMessage *msg;

  /* We call this function to do the actual work */
  msg = parse_ordered_list_into_log_message_no_check(ordered_list);

  /* But in this function we make sure that parsing did not fail */
  cr_assert_not_null(msg, "expected ordered-parser success and it returned failure, ordered list=%s", ordered_list);

  return msg;
}

static LogMessage *
parse_ordered_list_into_log_message_no_check(const gchar *ordered_list)
{
  LogMessage *msg;
  LogPathOptions path_options = LOG_PATH_OPTIONS_INIT;
  LogParser *cloned_parser;

  /* First get a copy of our parser */
  cloned_parser = (LogParser *) log_pipe_clone(&ordered_parser->super);

  /* Set the ${MESSAGE} part of our dummy log message */
  msg = log_msg_new_empty();
  log_msg_set_value(msg, LM_V_MESSAGE, ordered_list, -1);

  /* Give our dummy log message to the parser for parsing */
  if (!log_parser_process_message(cloned_parser, &msg, &path_options))
    {
      /* Cleanup in case of failure */
      log_msg_unref(msg);
      log_pipe_unref(&cloned_parser->super);
      return NULL;
    }

  log_pipe_unref(&cloned_parser->super);
  return msg;
}

/* Start syslog-ng; create and initialise the global OrderedParser */
void
setup(void)
{
  app_startup();
  ordered_parser = ordered_parser_new(NULL);
  log_pipe_init((LogPipe *)ordered_parser);
}

/* Deinitialise and free the global OrderedParser; stop syslog-ng */
void
teardown(void)
{
  log_pipe_deinit((LogPipe *)ordered_parser);
  log_pipe_unref(&ordered_parser->super);
  scratch_buffers_explicit_gc();
  app_shutdown();
}
```

The general structure for our unit tests is as follows:
1. Set any ordered-parser options or flags.
2. Call the parse function we wrote above, with our `${MESSAGE}` to test.
3. Call the `libtest/` assert function to check that our message was properly parsed.

When testing involves repeating the same logic over different sets of parameters, it is usually a good idea to use Criterion's parameterized tests. This is covered in the filter function section of this guide.
```
Test(ordered_parser, basic_default)
{
  LogMessage *msg;

  msg = parse_ordered_list_into_log_message("A) Apple");
  assert_log_message_value_by_name(msg, "A", "Apple");
  log_msg_unref(msg);
}

Test(ordered_parser, letters)
{
  LogMessage *msg;

  ordered_parser_process_flag(ordered_parser, "letters");
  msg = parse_ordered_list_into_log_message("A) Apple B) Banana C) Cherry");
  assert_log_message_value_by_name(msg, "A", "Apple");
  assert_log_message_value_by_name(msg, "B", "Banana");
  assert_log_message_value_by_name(msg, "C", "Cherry");
  log_msg_unref(msg);
}

/* Other tests omitted for brevity */

TestSuite(ordered_parser, .init = setup, .fini = teardown);
```
