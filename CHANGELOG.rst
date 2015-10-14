CHANGELOG
=========

This document describes changes between each past release.


1.1.0 (2015-10-14)
------------------

- Do not install postgresql dependencies by default.
- Add statsd metrics on SyncClient response status_code.
- Handle the new Firefox Sync sort=oldest parameter.
- Rename ids to in_ids to cope with Kinto protocol.
- Make sure Next-Page header keeps QueryString parameters.
- Add a Token server heartbeat.
- Remove the not accurate Total-Records when paginating.


1.0.0 (2015-10-06)
------------------

- First implementation of Syncto server.
- Connection with Token server and Sync servers.
- Encrypted credentials caching (#30, #31)
- Collections are Read-only by default
- Write permission on collection can be configured.
- Statsd monitoring for backends calls.
- Convert Syncto requests headers to Firefox Sync ones.
- Convert Firefox Sync headers to Syncto ones.
