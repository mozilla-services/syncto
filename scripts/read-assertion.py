#!/usr/bin/env python
# -*- coding: utf-8 -*-
import base64
import sys


def base64url_decode(input):
    rem = len(input) % 4
    if rem > 0:
        input += b'=' * (4 - rem)
    return base64.urlsafe_b64decode(input)

if len(sys.argv) < 2:
    print("USAGE: %s BID_ASSERTION" % sys.argv[0])
    sys.exit(1)

if __name__ == '__main__':
    assertion = sys.argv[1]

    print("---- BEGIN ASSERTION ----")

    for fragment in assertion.split('.'):
        try:
            decoded_fragment = base64url_decode(fragment)
        except TypeError:
            decoded_fragment = ''

        # Ignore signatures and cryptographic hashes
        if decoded_fragment.startswith('{'):
            print(decoded_fragment)

    print("---- END ASSERTION ----")
