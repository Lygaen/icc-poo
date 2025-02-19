from src.rational import *

def test_frac_to_str() -> None:
    assert frac_to_str(Rational(1, 2)) == "1/2"
    assert frac_to_str(Rational(5, 3)) == "5/3"
    assert frac_to_str(Rational(-1, 2)) == "-1/2"
    assert frac_to_str(Rational(-5, 3)) == "-5/3"
    assert frac_to_str(Rational(6, 1)) == "6"
    assert frac_to_str(Rational(-6, 1)) == "-6"

def test_reduce() -> None:
    assert reduce(Rational(1, 2)) == Rational(1, 2)
    assert reduce(Rational(4, 2)) == Rational(2, 1)
    assert reduce(Rational(-3, 2)) == Rational(-3, 2)
    assert reduce(Rational(-6, 2)) == Rational(-3, 1)

def test_add() -> None:
    assert add(Rational(1,2), Rational(1,3)) == Rational(5,6)
    assert add(Rational(2,2), Rational(3,3)) == Rational(2,1)
    assert add(Rational(3,2), Rational(1,2)) == Rational(2,1)

def test_substract() -> None:
    assert substract(Rational(1,2), Rational(1,3)) == Rational(1,6)
    assert substract(Rational(2,2), Rational(3,3)) == Rational(0,1)
    assert substract(Rational(1,2), Rational(5,6)) == Rational(-1,3)

def test_multiply() -> None:
    assert multiply(Rational(3,1), Rational(5,1)) == Rational(15,1)
    assert multiply(Rational(2,-3), Rational(1,-2)) == Rational(1,3)
    assert multiply(Rational(-3,2), Rational(4,5)) == Rational(-6,5)

def test_divide() -> None:
    assert divide(Rational(3,1), Rational(5,1)) == Rational(3,5)
    assert divide(Rational(2,-3), Rational(1,-2)) == Rational(4,3)
    assert divide(Rational(-3,2), Rational(4,5)) == Rational(-15,8)