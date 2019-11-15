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
    print('the callable string:', python_callable_string)
    query = ''
    union_statement = None
    if 'union' in python_callable_string:
        union_portion = python_callable_string.split('union')[1]
        the_first_portion = python_callable_string.split('union')[0]
        python_callable_string = the_first_portion
        removed_opening_bracket = union_portion.split('(')[1]
        second_table = removed_opening_bracket.split('.')[0]
        projection_portion = union_portion.split('projection')[1]
        without_opening_bracket = projection_portion.split('(')[1]
        props = without_opening_bracket.split(')', 1)[0].replace('"', '')
        query = 'select {props} from {table_two}'.format(props=props, table_two=second_table)
        union_statement = query

    difference_statement = None
    if 'difference' in python_callable_string:
        difference_portion = python_callable_string.split('difference')[1]
        the_first_portion = python_callable_string.split('difference')[0]
        python_callable_string = the_first_portion
        removed_opening_bracket = difference_portion.split('(')[1]
        second_table = removed_opening_bracket.split('.')[0]
        projection_portion = difference_portion.split('projection')[1]
        without_opening_bracket = projection_portion.split('(')[1]
        props = without_opening_bracket.split(')', 1)[0].replace('"', '')
        query = '{query} left join {table_two} using ({prop}) where {table_two}.{prop} is null'.format(
            query=query,
            table_two=second_table,
            prop=props
        )
        difference_statement = query

    selection_query = None
    if 'selection' in python_callable_string:
        selection_portion = python_callable_string.split('selection')[1]
        select_clause = selection_portion.split('(')[1]
        condition = select_clause.split(')', 1)[0].replace("'", '')
        if '∨' in condition:
            condition = condition.replace('∨', 'or')
        if '∧' in condition:
            condition = condition.replace('∧', 'and')
        selection_query = 'where {}'.format(condition)

    query = 'select *'
    if 'projection' in python_callable_string:
        projection_portion = python_callable_string.split('projection')[1]
        operation_the_other_string = projection_portion.split('(')[1]
        props = operation_the_other_string.split(')', 1)[0].replace('"', '')
        query = 'select {}'.format(props)

    # Mysql does not have a product statement, but the same can be simulated using
    # a cross join statement  http://www.mysqltutorial.org/mysql-cross-join/
    # some product statements
    # ?query=(Books * Articles) : this is a very simple cross join statement
    # ?query=σauthor = 'tutorialspoint'(Books * Articles) : this is a bit complex, using product together with selection
    # ?query=π author (σauthor = 'tutorialspoint'(Books * Articles)) : this is very complex, uses both selection
    # and projection together product operators
    cross_join_statement = None
    if 'product' in python_callable_string:
        product_portion = python_callable_string.split('product')[1]
        product_clause = product_portion.split('(')[1]
        second_table = product_clause.split(')', 1)[0]
        cross_join_statement = 'cross join {second_table}'.format(second_table=second_table)

    query = "{query} from {table_name}".format(query=query, table_name=python_callable_string.split('.')[0])

    if cross_join_statement:
        query = "{query} {statement}".format(query=query, statement=cross_join_statement)

    if selection_query:
        query = "{query} {selection_query}".format(
            query=query,
            selection_query=selection_query)

    if union_statement:
        query = "{query} union {union_statement}".format(query=query, union_statement=union_statement)

    if difference_statement:
        query = "{query} {difference_statement}".format(query=query, difference_statement=difference_statement)
    return query
