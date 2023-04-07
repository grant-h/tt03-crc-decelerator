#!/usr/bin/env python3
import sys

if len(sys.argv) < 2:
    sys.exit(1)

with open(sys.argv[1], 'rb') as fp:
    data = fp.read()
    data_new = data.replace(b"</defs><g", b'</defs><rect width="100%" height="100%" fill="white"/><g')

if data != data_new:
    print("Writing new SVG")
    with open(sys.argv[1], 'wb') as fp:
        fp.write(data_new)
