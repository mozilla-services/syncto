Installation
############


Run locally
===========

*Sycnto* is based on top of the `cliquet <https://cliquet.rtfd.org>`_ project, and
as such, please refer to cliquet's documentation for more details.


For development
---------------

By default, *Sycnto* persists internal cache in Redis.

::

    make serve

Authentication
--------------

By default, *Sycnto* relies on Firefox Account OAuth2 Bearer tokens to authenticate
users.

See `cliquet documentation <http://cliquet.readthedocs.org/en/latest/configuration.html#authentication>`_
to configure authentication options.

Note that you will also need to pass through a BrowserID assertion in
order for Syncto to read the Firefox Sync server.


Install and setup PostgreSQL
============================

 (*requires PostgreSQL 9.3 or higher*).


Using Docker
------------

::

    docker run -e POSTGRES_PASSWORD=postgres -p 5434:5432 postgres


Linux
-----

On debian / ubuntu based systems:

::

    apt-get install postgresql postgresql-contrib


By default, the ``postgres`` user has no password and can hence only connect
if ran by the ``postgres`` system user. The following command will assign it:

::

    sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'postgres';"


OS X
----

Assuming `brew <http://brew.sh/>`_ is installed:

::

    brew update
    brew install postgresql

Create the initial database:

::

    initdb /usr/local/var/postgres


Cryptography libraries
======================

Linux
-----

On Debian / Ubuntu based systems::

    apt-get install libffi-dev libssl-dev

On RHEL-derivatives::

    apt-get install libffi-devel openssl-devel

OS X
----

Assuming `brew <http://brew.sh/>`_ is installed:

::

    brew install libffi openssl pkg-config


Running in production
=====================

Recommended settings
--------------------

Most default setting values in the application code base are suitable for production.

But the set of settings mentionned below might deserve some review or adjustments:


.. code-block :: ini

    cliquet.http_scheme = https
    cliquet.paginate_by = 100
    cliquet.batch_max_requests = 25
    cliquet.delete_collection_enabled = false
    cliquet.storage_pool_maxconn = 50
    cliquet.cache_pool_maxconn = 50
    fxa-oauth.cache_ttl_seconds = 3600

:note:

    For an exhaustive list of available settings and their default values,
    refer to `cliquet source code <https://github.com/mozilla-services/cliquet/blob/2.3.1/cliquet/__init__.py#L26-L78>`_.


Monitoring
----------

.. code-block :: ini

    # Heka
    cliquet.logging_renderer = cliquet.logs.MozillaHekaRenderer

    # StatsD
    cliquet.statsd_url = udp://carbon.server:8125

Application output should go to ``stdout``, and message format should have no
prefix string:


.. code-block :: ini

    [handler_console]
    class = StreamHandler
    args = (sys.stdout,)
    level = INFO
    formater = heka

    [formatter_heka]
    format = %(message)s


Adapt the logging configuration in order to plug Sentry:

.. code-block:: ini

    [loggers]
    keys = root, sentry

    [handlers]
    keys = console, sentry

    [formatters]
    keys = generic

    [logger_root]
    level = INFO
    handlers = console, sentry

    [logger_sentry]
    level = WARN
    handlers = console
    qualname = sentry.errors
    propagate = 0

    [handler_console]
    class = StreamHandler
    args = (sys.stdout,)
    level = INFO
    formater = heka

    [formatter_heka]
    format = %(message)s

    [handler_sentry]
    class = raven.handlers.logging.SentryHandler
    args = ('http://public:secret@example.com/1',)
    level = WARNING
    formatter = generic

    [formatter_generic]
    format = %(asctime)s,%(msecs)03d %(levelname)-5.5s [%(name)s] %(message)s
    datefmt = %H:%M:%S


PostgreSQL setup
----------------

In production, it is wise to run the application with a dedicated database and
user.

::

    postgres=# CREATE USER produser;
    postgres=# CREATE DATABASE proddb OWNER produser;
    CREATE DATABASE


The tables needs to be created with the `cliquet` tool.

.. code-block :: bash

    $ cliquet --ini config/syncto.ini migrate

:note:

    Alternatively the SQL initialization files can be found in the
    *cliquet* source code (``cliquet/cache/postgresql/schemal.sql`` and
    ``cliquet/storage/postgresql/schemal.sql``).


Running with uWsgi
------------------

To run the application using uWsgi, an **app.wsgi** file is provided.
This command can be used to run it::

    uwsgi --ini config/syncto.ini

uWsgi configuration can be tweaked in the ini file in the dedicated
**[uwsgi]** section.

Here's an example:

.. code-block :: ini

    [uwsgi]
    wsgi-file = app.wsgi
    enable-threads = true
    http-socket = 127.0.0.1:8000
    processes =  3
    master = true
    module = syncto
    harakiri = 30
    uid = syncto
    gid = syncto
    virtualenv = .
    lazy = true
    lazy-apps = true


To use a different ini file, the ``SYNCTO_INI`` environment variable
should be present with a path to it.
