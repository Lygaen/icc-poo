from src.derivatives import *
import pytest

def test_tree_leaf() -> None:
    assert tree_leaf("").value == ""
    assert tree_leaf("*").value == "*"
    assert tree_leaf("*").right == None
    assert tree_leaf("/").left == None

def test_tree_to_str() -> None:
    assert tree_to_str(Tree(
        tree_leaf("x"),
        tree_leaf("a"),
        "+",
    )) == "((x) + (a))"

    assert tree_to_str(Tree(
        Tree(tree_leaf("x"), tree_leaf("a"), "+"),
        Tree(tree_leaf("x"), tree_leaf("b"), "+"),
        "*",
    )) == "(((x) + (a)) * ((x) + (b)))"

    assert tree_to_str(Tree(
        Tree(Tree(tree_leaf("x"), tree_leaf("x"), "*"),
              tree_leaf("x"), "*"),
        Tree(tree_leaf("a"), tree_leaf("x"), "*"),
        "+",
    )) == "((((x) * (x)) * (x)) + ((a) * (x)))"
    
    assert tree_to_str(Tree(
        Tree(tree_leaf("x"), tree_leaf("a"), "^"),
        Tree(
            Tree(tree_leaf("x"), tree_leaf("x"), "*"),
            Tree(tree_leaf("b"), tree_leaf("x"), "*"),
            "+",
        ),
        "/",
    )) == "(((x) ^ (a)) / (((x) * (x)) + ((b) * (x))))"

def test_tree_is_leaf() -> None:
    assert tree_is_leaf(tree_leaf(" "))
    assert tree_is_leaf(Tree(None, None, "/"))
    assert not tree_is_leaf(Tree(tree_leaf("x"), None, "*"))
    assert not tree_is_leaf(Tree(None, tree_leaf("x"), "*"))
    assert not tree_is_leaf(Tree(tree_leaf("x"), tree_leaf("x"), "*"))

def test_derivative() -> None:
    xval = tree_leaf("x")
    aval = tree_leaf("a")
    one = tree_leaf("1")
    zero = tree_leaf("0")

    assert derivative(xval) == one
    assert derivative(aval) == zero
    assert derivative(Tree(xval, aval, "+")
                      ) == Tree(one, zero, "+")
    assert derivative(Tree(xval, aval, "-")
                      ) == Tree(one, zero, "-")
    assert derivative(Tree(xval, aval, "*")
                      ) == Tree(Tree(one, aval, "*"), Tree(xval, zero, "*"), "+")
    assert derivative(Tree(xval, aval, "/")
                      ) == Tree(Tree(one, aval, "*"), Tree(xval, zero, "*"), "-")
    assert derivative(Tree(xval, aval, "^")
                      ) == Tree(Tree(aval, one, "*"), Tree(xval, Tree(aval, one, "-"), "^"), "*")
    
    with pytest.raises(ValueError):
        derivative(Tree(xval, Tree(xval, xval, "+"), "^"))
    
    with pytest.raises(ValueError):
        derivative(Tree(xval, xval, "//"))