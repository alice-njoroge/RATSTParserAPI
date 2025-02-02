# -*- coding: utf-8 -*-
# RATST Parser
#
# This module implements a parser for relational algebra, and can be used
# to convert expressions into python expressions and to get the parse-tree
# of the expression.
#
from typing import Optional, Union, List, Any

import rtypes

RELATION = 0
UNARY = 1
BINARY = 2

PRODUCT = '*'
DIFFERENCE = '-'
UNION = '∪'
INTERSECTION = '∩'
DIVISION = '÷'
JOIN = '⋈'
JOIN_LEFT = '⧑'
JOIN_RIGHT = '⧒'
JOIN_FULL = '⧓'
PROJECTION = 'π'
SELECTION = 'σ'
RENAME = 'ρ'
ARROW = '➡'

b_operators = (PRODUCT, DIFFERENCE, UNION, INTERSECTION, DIVISION,
               JOIN, JOIN_LEFT, JOIN_RIGHT, JOIN_FULL)  # List of binary operators
u_operators = (PROJECTION, SELECTION, RENAME)  # List of unary operators

# Associates operator with python method
op_functions = {
    PRODUCT: 'product', DIFFERENCE: 'difference', UNION: 'union', INTERSECTION: 'intersection', DIVISION: 'division',
    JOIN: 'join',
    JOIN_LEFT: 'outer_left', JOIN_RIGHT: 'outer_right', JOIN_FULL: 'outer', PROJECTION: 'projection',
    SELECTION: 'selection', RENAME: 'rename'}


class TokenizerException(Exception):
    pass


class ParserException(Exception):
    pass


class CallableString(str):
    """
    This is a string. However it is also callable.

    For example:
    CallableString('1+1')()
    returns 2

    It is used to contain Python expressions and print
    or execute them.
    """

    def __call__(self, context=None):
        """
        context is a dictionary where to
        each name is associated the relative relation
        """
        return eval(self, context)


class Node:
    """This class is a node of a relational expression. Leaves are relations
    and internal nodes are operations.

    The 'kind' property indicates whether the node is a binary operator, unary
    operator or relation.
    Since relations are leaves, a relation node will have no attribute for
    children.

    If the node is a binary operator, it will have left and right properties.

    If the node is a unary operator, it will have a child, pointing to the
    child node and a property containing the string with the props of the
    operation.

    This class is used to convert an expression into python code."""
    kind = None  # type: Optional[int]
    __hash__ = None  # type: None

    def __init__(self, expression: Optional[list] = None) -> None:
        """Generates the tree from the tokenized expression
        If no expression is specified then it will create an empty node"""
        print("inside init of node this is the express:", expression)
        if expression is None or len(expression) == 0:
            return

        # If the list contains only a list, it will consider the lower level list.
        # This will allow things like ((((((a))))) to work
        while len(expression) == 1 and isinstance(expression[0], list):
            expression = expression[0]

        # The list contains only 1 string. Means it is the name of a relation
        if len(expression) == 1:
            self.kind = RELATION
            self.name = expression[0]
            if not rtypes.is_valid_relation_name(self.name):
                raise ParserException(
                    u"'%s' is not a valid relation name" % self.name)
            return

        # Expression from right to left, searching for binary operators
        # this means that binary operators have lesser priority than
        # unary operators.
        # It finds the operator with lesser priority, uses it as root of this
        # (sub)tree using everything on its left as left parameter (so building
        # a left subtree with the part of the list located on left) and doing
        # the same on right.
        # Since it searches for strings, and expressions into parenthesis are
        # within sub-lists, they won't be found here, ensuring that they will
        # have highest priority.
        for i in range(len(expression) - 1, -1, -1):
            if expression[i] in b_operators:  # Binary operator
                self.kind = BINARY
                self.name = expression[i]

                if len(expression[:i]) == 0:
                    raise ParserException(
                        u"Expected left operand for '%s'" % self.name)

                if len(expression[i + 1:]) == 0:
                    raise ParserException(
                        u"Expected right operand for '%s'" % self.name)

                self.left = node(expression[:i])
                self.right = node(expression[i + 1:])
                return
        '''Searches for unary operators, parsing from right to left'''
        for i in range(len(expression) - 1, -1, -1):
            if expression[i] in u_operators:  # Unary operator
                self.kind = UNARY
                self.name = expression[i]

                if len(expression) <= i + 2:
                    raise ParserException(
                        u"Expected more tokens in '%s'" % self.name)

                self.prop = expression[1 + i].strip()
                self.child = node(expression[2 + i])

                return
        raise ParserException("Expected operator in '%s'" % expression)

    
    def toPython(self) -> CallableString:
        """This method converts the AST into a python code string, which
        will require the relation module to be executed.

        The return value is a CallableString, which means that it can be
        directly called."""
        return CallableString(self._toPython())

    def _toPython(self) -> str:
        """
        Same as toPython but returns a regular string
        """
        if self.name in b_operators:
            print('the left side of binary  operators:', self.left.toPython())
            return '%s.%s(%s)' % (self.left.toPython(), op_functions[self.name], self.right.toPython())
        elif self.name in u_operators:
            print('props:', self.prop)
            prop = self.prop

            # Converting parameters
            if self.name == PROJECTION:
                prop = '\"%s\"' % prop.replace(' ', '').replace(',', '\",\"')
            elif self.name == RENAME:
                prop = '{\"%s\"}' % prop.replace(
                    ',', '\",\"').replace(ARROW, '\":\"').replace(' ', '')
            else:  # Selection
                prop = repr(prop)

            return '%s.%s(%s)' % (self.child.toPython(), op_functions[self.name], prop)
        return self.name

    def printtree(self, level: int = 0) -> str:
        """returns a representation of the tree using indentation"""
        r = ''
        for i in range(level):
            r += '  '
        r += self.name
        if self.name in b_operators:
            r += self.left.printtree(level + 1)
            r += self.right.printtree(level + 1)
        elif self.name in u_operators:
            r += '\t%s\n' % self.prop
            r += self.child.printtree(level + 1)
        return '\n' + r

    def get_left_leaf(self) -> 'Node':
        '''This function returns the leftmost leaf in the tree.'''
        if self.kind == RELATION:
            return self
        elif self.kind == UNARY:
            return self.child.get_left_leaf()
        elif self.kind == BINARY:
            return self.left.get_left_leaf()
        raise ValueError('What kind of alien object is this?')


    def __eq__(self, other):
        if not (isinstance(other, node) and self.name == other.name and self.kind == other.kind):
            return False

        if self.kind == UNARY:
            if other.prop != self.prop:
                return False
            return self.child == other.child
        if self.kind == BINARY:
            return self.left == other.left and self.right == other.right
        return True

    def __str__(self):
        if self.kind == RELATION:
            return self.name
        elif self.kind == UNARY:
            return self.name + " " + self.prop + " (" + self.child.__str__() + ")"
        elif self.kind == BINARY:
            le = self.left.__str__()
            if self.right.kind != BINARY:
                re = self.right.__str__()
            else:
                re = "(" + self.right.__str__() + ")"
            return le + self.name + re
        raise ValueError('What kind of alien object is this?')


def _find_matching_parenthesis(expression: str, start=0, openpar=u'(', closepar=u')') -> Optional[int]:
    """This function returns the position of the matching
    close parenthesis to the 1st open parenthesis found
    starting from start (0 by default)"""
    par_count = 0  # Count of parenthesis

    string = False
    escape = False

    for i in range(start, len(expression)):
        if expression[i] == '\'' and not escape:
            string = not string
        if expression[i] == '\\' and not escape:
            escape = True
        else:
            escape = False
        if string:
            continue

        if expression[i] == openpar:
            par_count += 1
        elif expression[i] == closepar:
            par_count -= 1
            if par_count == 0:
                return i  # Closing parenthesis of the parameter
    return None


def _find_token(haystack: str, needle: str) -> int:
    """
    Like the string function find, but
    ignores tokens that are within a string
    literal.
    """
    r = -1
    string = False
    escape = False

    for i in range(len(haystack)):
        if haystack[i] == '\'' and not escape:
            string = not string
        if haystack[i] == '\\' and not escape:
            escape = True
        else:
            escape = False
        if string:
            continue

        if haystack[i:].startswith(needle):
            return i
    return r


def tokenize(expression: str) -> list:
    """This function converts a relational expression into a list where
    every token of the expression is an item of a list. Expressions into
    parenthesis will be converted into sub lists."""

    # List for the tokens
    print('inside the tokenize expression', expression)
    items = []  # type: List[Union[str,list]]

    expression = expression.strip()  # Removes initial and ending spaces

    while len(expression) > 0:
        if expression.startswith('('):  # Parenthesis state
            print('inside tokenize function and it starts with (')
            end = _find_matching_parenthesis(expression)
            print('then the ending bracket:', end)
            if end is None:
                raise TokenizerException(
                    "Missing matching ')' in '%s'" % expression)
            # Appends the tokenization of the content of the parenthesis
            print('content of parenthesis to be  tokenized:', expression[1:end])
            items.append(tokenize(expression[1:end]))
            print('then the items are:', items)
            # Removes the entire parenthesis and content from the expression
            expression = expression[end + 1:].strip()
            print('so the final expression is:', expression)

        elif expression.startswith((SELECTION, RENAME, PROJECTION)):  # Unary operators
            print('else the expression starts with either selection, rename or projection')
            print('append the unary operator to the array:', expression[0:1])
            items.append(expression[0:1])
            # Adding operator in the top of the list
            expression = expression[1:].strip()  # Removing operator from the expression
            print('remove the operator from the new parenthesis:', expression)

            if expression.startswith('('):  # Expression with parenthesis, so adding what's between open and close without tokenization
                par = expression.find( '(', _find_matching_parenthesis(expression))
                print('So the remaining expression check if it starts with a paranthesis:', par)
            else:  # Expression without parenthesis, so adding what's between start and parenthesis as whole
                par = _find_token(expression, '(')
                print('It does not start with a parenthesis so pick everything:', par)

            print('so pick everything from that index:', expression[:par].strip())
            items.append(expression[:par].strip())
            print('append everything found to the items array:', items)
            # Inserting parameter of the operator
            expression = expression[par:].strip()  # Removing parameter from the expression
            print('the remove what we found from the original expression given')
        else:  # Relation (hopefully)
            expression += ' '  # To avoid the special case of the ending

            # Initial part is a relation, stop when the name of the relation is
            # over
            for r in range(1, len(expression)):
                if rtypes.RELATION_NAME_REGEXP.match(expression[:r + 1]) is None:
                    break
            print('all other statements were false so:', expression[:r])
            items.append(expression[:r])
            expression = expression[r:].strip()
    return items


def tree(expression: str) -> Node:
    """This function parses a relational algebra expression into a AST and returns
    the root node using the Node class."""
    print('inside the tree function:', expression)
    return Node(tokenize(expression))


def parse(expr: str) -> CallableString:
    """This function parses a relational algebra expression, and returns a
    CallableString (a string that can be called) with the corresponding
    Python expression.
    """
    print('inside parse function:', expr)
    print('the tree:\n', tree(expr).printtree(level=5))
    return tree(expr).toPython()


# Backwards compatibility
node = Node

if __name__ == "__main__":
    while True:
        e = input("Expression: ")
        print(parse(e))
