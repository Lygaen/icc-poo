from dataclasses import dataclass

@dataclass(frozen=True)
class Rational:
    p: int = 0
    q: int = 1

def frac_to_str(v: Rational) -> str:
    return f"{v.p}{"/" + str(v.q) if v.q != 1 else ""}"

def pgcd(a: int, b: int) -> int:
    while b != 0:
        r = a % b
        a = b
        b = r
    return a

def reduce(v: Rational) -> Rational:
    divisor = pgcd(v.p, v.q)
    return Rational(v.p // divisor, v.q // divisor)

def add(r1: Rational, r2: Rational) -> Rational:
    return reduce(Rational(r1.p*r2.q + r2.p*r1.q, r1.q*r2.q))

def substract(r1: Rational, r2: Rational) -> Rational:
    return reduce(Rational(r1.p*r2.q - r2.p*r1.q, r1.q*r2.q))

def multiply(r1: Rational, r2: Rational) -> Rational:
    return reduce(Rational(r1.p*r2.p, r1.q*r2.q))

def divide(r1: Rational, r2: Rational) -> Rational:
    return reduce(Rational(r1.p*r2.q,r1.q*r2.p))