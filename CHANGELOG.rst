CHANGELOG
=========

This document describes changes between each past release.


1.5.0 (2016-01-27)
------------------

**Protocol**

- Make sure batch always return 200 except for 5xx errors. (#78)

**Bug fixes**

- Fix ``If-None-Match`` header format which doesn't take quote around the ``*`` parameter. (#76)

**Internal changes**

- Add a Dockerfile (#77)
- Remove documentation warnings (#74)


1.4.0 (2015-11-17)
------------------

- Upgraded to *Cliquet* 2.11.0

**New Features**

- Pass User-Agent header to sync. (#68)
- Add trusted certificate pinning support. (#72)

See also `*Cliquet* changes <https://github.com/mozilla-services/cliquet/releases/2.11.0>`_


1.3.0 (2015-10-27)
------------------

- Upgraded to *Cliquet* 2.9.0

**Protocol**

- Client-state id should now be provided through the bucket id in the
  URL (#62)


1.2.0 (2015-10-22)
------------------

- Send ``Cache-Control: no-cache`` header (#54)
- Make sure collection_list return an empty list (#56)


1.1.0 (2015-10-14)
------------------

- Do not install postgresql dependencies by default.
- Add statsd metrics on SyncClient response status_code. (#49)
- Handle the new Firefox Sync sort=oldest parameter. (#46)
- Rename ids to in_ids to reflect the Kinto protocol. (#50)
- Make sure Next-Page header keeps QueryString parameters. (#47)
- Add a Token server heartbeat. (#44)
- Remove the not accurate Total-Records header when paginating. (#43)
- Expose the now deprecated cliquet.batch_max_requests settings. (#48)


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
