# -*- coding: utf-8 -*-
# RATST Parser
#
# This module implements a parser for relational algebra, and can be used
# to convert expressions into python expressions and to get the parse-tree
# of the expression.
#


def to_mysql(python_callable_string) -> str:
    """
    convert the python callable string to sql
    :param python_callable_string:
    :return:
    """
    print(python_callable_string)
    relation = python_callable_string.split('.')[0]
    the_other_string = python_callable_string.split('.')[1]
    operation = the_other_string.split('(')[0]
    print('the other string', the_other_string.split('(')[1])
    if operation == 'selection' and 'projection' in the_other_string.split('(')[1]:
        print('the other string:', the_other_string)
    if operation == 'selection':
        operation_the_other_string = the_other_string.split('(')[1]
        condition = operation_the_other_string.split(')', 1)[0].replace("'", '')
        sql_statement = "select * from {relation} where {condition}".format(
            relation=relation,
            condition=condition)
        return sql_statement
    elif operation == 'projection':
        operation_the_other_string = the_other_string.split('(')[1]
        selection_list = operation_the_other_string.split(')', 1)[0].replace('"', '')
        sql_statement = "select {props_list} from {relation}".format(
            props_list=selection_list,
            relation=relation)
        return sql_statement
