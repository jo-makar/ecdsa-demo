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


if __name__ == '__main__':
    privkey = Privkey('privkey.pem')

    # FIXME generate a signature using the openssl and verify it here
    #       openssl dgst -ecdsa-with-SHA1 -sign private.pem test.pdf > signature.bin
    # FIXME generate a signature here and use openssl to verify it
    #       openssl dgst -ecdsa-with-SHA1 -verify public.pem -signature signature.bin test.pdf
