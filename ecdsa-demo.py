#!/usr/bin/env python3
# Elliptic Curve Digital Signature Algorithm demo
# 
# Create a private Elliptic Curve private key:
# (with 256-bit prime field Weierstrass curve, eg y^2 = x^3 + ax + b)
#     openssl ecparam -name prime256v1 -genkey -out privkey.pem
#
# And create the corresponding public key:
#     openssl ec -in privkey.pem -pubout >pubkey.pem


from key import Privkey, Pubkey
from point import modinv

import hashlib
import os
import random
import struct
import subprocess


if __name__ == '__main__':
    privkey = Privkey('privkey.pem')
    pubkey = Pubkey('pubkey.pem')

    for attr in ['a', 'b', 'g', 'n', 'p']:
        assert getattr(privkey, attr) == getattr(pubkey, attr)
    assert pubkey.pubkey == privkey.d * privkey.g

    #
    # (OpenSSL) Signature verification demo
    #

    cmd = ['openssl', 'dgst', '-sha256', '-sign', 'privkey.pem', 'README.md']
    output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)

    # (Crude) Signature ASN.1 parsing
    # ... | openssl asn1parse -inform der

    assert output[0] == 0x30 # Sequence
    assert output[1] == len(output) - 2

    bytes_to_int = lambda b: int(b.hex(), 16)

    assert output[2] == 0x02 # Integer
    r = bytes_to_int(output[4 : 4 + output[3]])

    i = 4 + output[3]
    assert output[i] == 0x02
    s = bytes_to_int(output[i+2 : i+2 + output[i+1]])
    assert i+2 + output[i+1] == len(output)

    n = pubkey.n
    g = pubkey.g
    pub = pubkey.pubkey

    with open('README.md') as file:
        buf = file.read().encode('utf-8')
        h = int(hashlib.sha256(buf).hexdigest(), 16) % n

    w = modinv(s, n)
    u = (w * h) % n
    v = (w * r) % n

    q = u*g + v*pub
    assert q.x == r
    print('openssl signature verified')

    #
    # Signature generation demo, OpenSSL verification
    #

    d = privkey.d
    n = privkey.n
    g = privkey.g

    with open('README.md') as file:
        buf = file.read().encode('utf-8')
        h = int(hashlib.sha256(buf).hexdigest(), 16) % n

    k = random.SystemRandom().randrange(1, n)
    q = k * g
    r = q.x % n
    s = ((h + r*d) * modinv(k, n)) % n

    def int_to_bytes(i: int) -> bytes:
        s = b''
        while True:
            s = struct.pack('B', i & 0xff) + s
            i >>= 8
            if i == 0:
                break

        # Ensure integers are not interpreted as negative
        if s[0] & 0x80 != 0:
            s = b'\x00' + s

        return s

    rb = int_to_bytes(r)
    sb = int_to_bytes(s)
    with open('sig.der', 'wb') as file:

        # (Crude) Signature ASN1. generation

        file.write(struct.pack('B', 0x30)) # Sequence
        file.write(struct.pack('B', 2 + len(rb) + 2 + len(sb)))

        file.write(struct.pack('B', 0x02)) # Integer
        file.write(struct.pack('B', len(rb)))
        file.write(rb)

        file.write(struct.pack('BB', 0x02, len(sb)))
        file.write(sb)


    cmd = ['openssl', 'dgst', '-sha256', '-verify', 'pubkey.pem', '-signature', 'sig.der', 'README.md']
    output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, encoding='utf-8')
    assert output.strip() == 'Verified OK'
    print('signature verified with openssl')
    os.remove('sig.der')
