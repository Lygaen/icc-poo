from dataclasses import dataclass

type NullableTree = 'Tree' | None

@dataclass(frozen=True)
class Tree:
    left: NullableTree
    right: NullableTree
    value: str # TODO Use enum instead

# TODO tree_simplify to simplify a tree (csts,...)

def tree_leaf(value: str) -> Tree:
    return Tree(None, None, value)

def tree_to_str(tree: Tree) -> str:
    left = "" if tree.left is None else tree_to_str(tree.left) + " "
    right = "" if tree.right is None else " " +tree_to_str(tree.right)
    return f"({left}{tree.value}{right})"

# [x] Support for latex stringify
# [ ] Test and coverage
# def tree_to_latex(tree: NullableTree) -> str:
#     if tree is None:
#         return ""
#     if tree_is_leaf(tree):
#         return tree.value
#     match tree.value:
#         case "+":
#             return f"{{{tree_to_latex(tree.left)}}}+{{{tree_to_latex(tree.right)}}}"
#         case "-":
#             return f"{{{tree_to_latex(tree.left)}}}-{{{tree_to_latex(tree.right)}}}"
#         case "*":
#             return f"{{{tree_to_latex(tree.left)}}} \\times {{{tree_to_latex(tree.right)}}}"
#         case "/":
#             return f"\\frac{{{tree_to_latex(tree.left)}}}{{{tree_to_latex(tree.right)}}}"
#         case "^":
#             return f"{{{tree_to_latex(tree.left)}}}^{{{tree_to_latex(tree.right)}}}"
#         case _:
#             raise ValueError(f"Invalid operator '{tree.value}'")

def tree_is_leaf(tree: Tree) -> bool:
    return tree.left is None and tree.right is None

def derivative(tree: Tree) -> Tree:
    if tree_is_leaf(tree):
        if tree.value == "x":
            return tree_leaf("1")
        else:
            return tree_leaf("0")
    
    dl: NullableTree = None
    if tree.left is not None:
        dl = derivative(tree.left)
    dr: NullableTree = None
    if tree.right is not None:
        dr = derivative(tree.right)

    match tree.value:
        case "+":
            return Tree(dl, dr, "+")
        case "-":
            return Tree(dl, dr, "-")
        case "*":
            return Tree(
                Tree(dl, tree.right, "*"),
                Tree(tree.left, dr, "*"),
                "+")
        case "/":
            return Tree(
                Tree(dl, tree.right, "*"),
                Tree(tree.left, dr, "*"),
                "-")
        case "^":
            if tree.right is None or not tree_is_leaf(tree.right):
                raise ValueError("Exponentiation derivation bad argument")

            return Tree(
                Tree(tree.right, dl, "*"),
                Tree(tree.left, Tree(tree.right, tree_leaf("1"), "-"), "^"),
                "*")
        case _:
            raise ValueError(f"Invalid operator '{tree.value}'")