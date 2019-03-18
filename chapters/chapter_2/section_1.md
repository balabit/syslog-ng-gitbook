# Fetching dependencies

[gh:glib]: http://github.com/GNOME/glib
[gh:flex]: https://github.com/westes/flex
[gh:openssl]: http://github.com/openssl/openssl
[ref:pkg-config]: http://www.freedesktop.org/wiki/Software/pkg-config/
[ref:libtool]: http://www.gnu.org/software/libtool/
[ref:automake]: http://www.gnu.org/software/automake/
[ref:bison]: http://www.gnu.org/software/bison/
[gh:eventlog]: https://github.com/balabit/eventlog
[ref:pcre]: http://www.pcre.org
[gh:ivykis]: http://github.com/buytenh/ivykis
[gh:json-c]: http://github.com/json-c/
[gh:rabbitmq-c]: http://github.com/alanxz/rabbitmq-c
[ref:docbook]: http://www.sagehill.net/docbookxsl/
[ref:astyle]: http://astyle.sourceforge.net/
[gh:criterion]: http://github.com/Snaipe/Criterion
[ref:libxml2]: http://www.xmlsoft.org/

Like every project, syslog-ng also uses other libraries and projects. 
That is why these dependencies must be fetched before compiling. 
In this section we list these libraries and version restrictions.

|Dependency                     |   Version    |
|-------------------------------|--------------|
|[glib][gh:glib]                |>=2.10.1      |
|[flex][gh:flex]                |>=2.0.0       |
|[openssl][gh:openssl]          |>=0.9.8       |
|[pkg-config][ref:pkg-config]   |---           |
|[libtool][ref:libtool]         |---           |
|[automake][ref:automake]       |>=2.4         |
|[bison][ref:bison]             |>=2.4         |
|[eventlog][gh:eventlog]        |>=0.2.12      |
|[pcre][ref:pcre]               |>=6.1         |
|[ivykis][gh:ivykis]            |>=0.36.1      |
|[json-c][gh:json-c]            |>=0.9         |
|[rabbitmq-c][gh:rabbitmq-c]    |>=0.6.0       |
|[docbook-xsl][ref:docbook]     |---           |

## Development dependencies

In case of contribution the following dependencies are required 
in order to run `make check`, `make style-check` and `make style-format`.

|Dependency                     |   Version    |
|-------------------------------|--------------|
|[astyle][ref:astyle]           |==3.1         |
|[criterion][gh:criterion]      |>=2.3.0       |
|[libxml2-utils][ref:libxml2]   |>=2.9.4       |
