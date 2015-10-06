Overview
#########

.. image:: images/overview-use-cases.png
    :align: right

*Syncto* is a bridge service that let you interract with the Firefox
Sync infrastructure using Kinto clients such as Kinto.js or Kinto.py.


More information
================

 - `The rationale behind Syncto on Mozilla Wiki <https://wiki.mozilla.org/Firefox_OS/Syncto>`_
 - `The documentation of the Firefox Sync project <https://docs.services.mozilla.com/storage/apis-1.5.html#collections>`_


.. _FAQ:

FAQ
===

Is Syncto secure?
-----------------

Syncto caches encrypted credentials for five minutes for a given
BrowserID assertion.

In addition all the data coming from Firefox Sync are encrypted and
Syncto will never have access to the encryption key (only final
clients have).

By default Syncto is a read-only proxy, to enable write permissions
for some collection, it has to be configured
explicitely. (history/password/tabs/etc.)


Is it web scale?
----------------

Syncto is simply a proxy that relies on the Firefox Sync
infrastructure.

Syncto doesn't even necessarily need a shared cache between its nodes.

Also it is better that nodes from the same loadbalancer uses the same
cache or that client are always affected to the same one with regards
to their Authorization header.


What is Cliquet? What is the difference between Cliquet, Syncto and Kinto ?
---------------------------------------------------------------------------

Cliquet is a toolkit for designing micro-services. Kinto and Syncto
are servers built using that toolkit.

Syncto uses the same protocol as Kinto does to name and interract with
collection records. This enable developers to use Kinto clients to
fetch Firefox Sync collection records.


I am seeing an Exception error, what's wrong?
---------------------------------------------

Have a look at the :ref:`Troubleshooting section <troubleshooting>` to
see what to do.
