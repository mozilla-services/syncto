Troubleshooting
###############

.. _troubleshooting:

We are doing the best we can so you do not have to read this section.

That said, we have included solutions (or at least explanations) for
some common problems below.

If you do not find a solution to your problem here, please
:ref:`ask for help <communication_channels>`!


OpenSSL error when installing on Mac OS X
=========================================

.. code-block:: bash

    #include <openssl/aes.h>
             ^
    1 error generated.
    error: command 'clang' failed with exit status 1

Apple has deprecated use of OpenSSL in favor of its own TLS and crypto
libraries, please
:ref:`refer to the installation documentation to fix this <osx-install-warning>`.
