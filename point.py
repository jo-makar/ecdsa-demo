from __future__ import annotations

from typing import Tuple, Union


class Curve:
    def __init__(self, a: int, b: int, p: int):
        self.a = a
        self.b = b
        self.p = p


    def __eq__(c: Curve, d: Curve) -> bool:
        return c.a == d.a and c.b == d.b and c.p == d.p

            
class Point:
    def __init__(self, src: Union[str, Tuple[int,int], None], curve: Curve):
        if isinstance(src, str):
            # Ref: https://stackoverflow.com/a/44827409
            assert len(src) == (1+64)*2
            assert src[0:2] == '04'
            self.x = int(src[2:66], 16)
            self.y = int(src[66:130], 16)
            self.at_inf = False

        elif isinstance(src, tuple):
            self.x, self.y = src
            self.at_inf = False
        
        elif src is None:
            self.x, self.y = None, None
            self.at_inf = True

        self.curve = curve

        if not self.at_inf:
            # Validate the defined point is indeed on the curve
            x, y, a, b, p = self.x, self.y, self.curve.a, self.curve.b, self.curve.p
            assert y**2 % p == (x**3 + a*x + b) % p


    def __eq__(p: Point, q: Point) -> bool:
        assert p.curve == q.curve

        if p.at_inf and q.at_inf:
            return True
        elif (p.at_inf and not q.at_inf) or (not p.at_inf and q.at_inf):
            return False
        else:
            return p.x == q.x and p.y == q.y


    def __add__(u: Point, v: Point) -> Point:
        assert u.curve == v.curve

        if u.at_inf and not v.at_inf:
            return Point((v.x, v.y), u.curve)
        elif not u.at_inf and v.at_inf:
            return Point((u.x, u.y), u.curve)
        elif u.at_inf and v.at_inf:
            return Point(None, u.curve)

        if u == v:
            return 2 * u
        elif u.x == v.x and u.y == -v.y:
            return Point(None, u.curve)

        p = u.curve.p
        m = ((v.y - u.y) * _modinv(v.x - u.x, p)) % p
        x = (m**2 - u.x - v.x) % p
        y = (m*(u.x - x) - u.y) % p
        return Point((x, y), u.curve)


    def _double(u: Point) -> Point:
        assert not u.at_inf

        a = u.curve.a
        p = u.curve.p
        m = ((3 * u.x**2 + a) * _modinv(2 * u.y, p)) % p
        x = (m**2 - 2*u.x) % p
        y = (m*(u.x - x) - u.y) % p
        return Point((x, y), u.curve)


    def __mul__(u: Point, k: int) -> Point:
        assert not u.at_inf
        assert k > 0

        a = u.curve.a
        p = u.curve.p

        w = Point((u.x, u.y), u.curve)
        l = 1

        cache = { 1: Point((u.x, u.y), u.curve) }

        while l < k:
            if l * 2 <= k:
                w = w._double()
                l *= 2

                cache[l] = Point((w.x, w.y), u.curve)

            else:
                for n in sorted(list(cache.keys()), reverse=True):
                    if l + n <= k:
                        w += cache[n]
                        l += n
                        break

        return w


    def __rmul__(p: Point, k: int) -> Point:
        return p.__mul__(k)


# Modular Inverse
# Find b such that (a * b) % m = 1
def _modinv(a: int, m: int) -> int:
    assert m > 1

    if a < 0:
        a += m
    elif a > m:
        a -= m
    assert 0 < a and a < m

    # The inverse will not exist unless a and m are coprime
    assert _gcd(a, m) == 1

    # Extended Euclidean algorithm
    # https://en.wikipedia.org/wiki/Extended_Euclidean_algorithm

    xi = 1
    yi = 0
    qi = 0
    ri = a*xi + m*yi

    xj = 0
    yj = 1
    qj = 0
    rj = a*xj + m*yj

    while True:
        qk = ri // rj
        rk = ri % rj
        xk = xi - qk*xj
        yk = yi - qk*yj

        if rk == 0:
            break

        qi, qj = qj, qk
        ri, rj = rj, rk
        xi, xj = xj, xk
        yi, yj = yj, yk

    assert rj == 1

    # rj = 1 = a*xj + m*yj => (a * xj) mod m = 1
    rv = xj

    if rv < 0:
        rv += m
    assert 0 < rv and rv < m
    return rv


# Greatest Common Denominator
def _gcd(u: int, v: int) -> int:
    assert u >= 0 and v >= 0

    if u == 0 and v == 0:
        return 0
    elif u == 0:
        return v
    elif v == 0:
        return u

    # Binary GCD algorithm
    # https://en.wikipedia.org/wiki/Binary_GCD_algorithm

    def trailing_zeros(i: int) -> int:
        assert i > 0

        b = 0
        j = i
        while j > 0:
            if j & 1 == 1:
                return b
            b += 1
            j >>= 1

    i = trailing_zeros(u); u >>= i
    j = trailing_zeros(v); v >>= j
    k = min(i, j)

    while True:
        if u > v:
            u, v = v, u

        v -= u

        if v == 0:
            return u << k

        v >>= trailing_zeros(v)


if __name__ == '__main__':
    curve = Curve(-2, 1, 89)
    p = Point((4, 18), curve)
    q = Point((15, 63), curve)
    r = p + q
    assert r.x == 86 and r.y == 43

    curve = Curve(2, 2, 17)
    p = Point((5, 1), curve)
    r = 2 * p
    assert r.x == 6 and r.y == 3
    s = 3 * p
    assert s.x == 10 and s.y == 6
    t = 18 * p
    assert t.x == 5 and t.y == 16
