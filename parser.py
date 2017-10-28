import json

from mypgparse import queryToJsonTree

SELECT_STMT = 'SelectStmt'
FROM_CLAUSE = 'fromClause'

RELATION_NAME = 'relname'
COLUMN_REF = 'ColumnRef'
FIELDS = 'fields'
JOIN_EXPR = 'JoinExpr'

RANGE_VAR = 'RangeVar'
LEFT_ARG = 'larg'
LEFT_EXPR = 'lexpr'
RIGHT_ARG = 'rarg'
RIGHT_EXPR = 'rexpr'
A_EXPR = 'A_Expr'
QUALIFIERS = 'quals'
NAME = 'name'
STRING_TYPE = 'String'
STR_TYPE = 'str'


class ColumnRef:
    def __init__(self, columnRefTree):
        fieldTree = columnRefTree[FIELDS]
        self.field = '.'.join([field[STRING_TYPE][STR_TYPE] for field in fieldTree])
        print('ColumnRef:', self.field)


class Expression:
    def __init__(self, exprTree):
        if COLUMN_REF in exprTree:
            column = exprTree[COLUMN_REF]
            # fields =
        print('Expression:', exprTree)


class JoinOp:
    def __init__(self, leftTable, leftCol, rightTable, rightCol, joinOperator):
        self.leftTable = leftTable
        self.leftColumn = leftCol
        self.rightTable = rightTable
        self.rightColumn = rightCol
        self.joinOperator = joinOperator

    @staticmethod
    def createJoinOp(joinExprTree):
        join = joinExprTree[QUALIFIERS][A_EXPR]
        operator = join[NAME]

        if type(operator) is list:
            operator = operator[0]

        operator = operator[STRING_TYPE][STR_TYPE]
        leftTable = joinExprTree[LEFT_ARG][RANGE_VAR][RELATION_NAME]
        rightTable = joinExprTree[RIGHT_ARG][RANGE_VAR][RELATION_NAME]
        leftExpr = join[LEFT_EXPR]
        leftCol = None
        rightCol = None

        if COLUMN_REF in leftExpr:
            leftCol = ColumnRef(leftExpr[COLUMN_REF])

        rightExpr = join[RIGHT_EXPR]
        if COLUMN_REF in rightExpr:
            rightCol = ColumnRef(rightExpr[COLUMN_REF])

        if leftTable is not None and rightTable is not None \
                and operator is not None and leftCol is not None \
                and rightCol is not None:
            return JoinOp(leftTable, leftCol.field,
                          rightTable, rightCol.field, operator)

    def __str__(self):
        return '{} join {} on {} {} {}'.format(
            self.leftTable, self.rightTable, self.leftColumn,
            self.joinOperator, self.rightColumn
        )


class JoinClause:
    def __init__(self, joinStr):
        self.joins = [JoinOp('...', '', '', '', ''), JoinOp('', '', '', '', '')]


class Query(object):
    def __init__(self, query):
        print(query, '\n')
        parseTree = json.loads(queryToJsonTree(query))
        if type(parseTree) is list and len(parseTree) == 1:
            parseTree = parseTree[0]

        if SELECT_STMT not in parseTree:
            raise ValueError('Expected a select statement')

        self.parseTree = parseTree
        self._parseFromClause(parseTree)
        self.joinClause = JoinClause('a join b on a.id = b.id join c on c.id = b.id')
        self.tables = {"a", "b", "c"}
        self.selectColumns = ["a.id", "b.id", "c.id"]

    def _parseFromClause(self, parseTree):
        select = parseTree[SELECT_STMT]
        fromClause = select[FROM_CLAUSE]
        self._parseJoins(fromClause)

    def _parseJoins(self, fromClause):
        joins = []
        tables = {}
        for clause in fromClause:
            joinExpr = clause[JOIN_EXPR]
            joins.append(self._parseJoinExpr(joinExpr))
            # left = self._parseJoinExpr(joinExpr[LEFT_ARG])
            # right = self._parseJoinExpr(joinExpr[RIGHT_ARG])

    def _parseJoinExpr(self, joinExpr):
        left = joinExpr[LEFT_ARG]
        print('LEFT:', left)

        if JOIN_EXPR in left:
            leftJoinExpr = left[JOIN_EXPR]
            print('leftJoinExpr:', leftJoinExpr, '\n')
            if QUALIFIERS in leftJoinExpr:
                join = JoinOp.createJoinOp(leftJoinExpr)
                print('Left join: ', str(join))


            else:
                leftJoins = self._parseJoinExpr(leftJoinExpr)
        else:
            print('No join expression in left tree:', left)
        # print()
        right = joinExpr[RIGHT_ARG]
        print('RIGHT:', right)

        if JOIN_EXPR in right:
            rightJoins = self._parseJoinExpr(right[JOIN_EXPR])
        else:
            print('No join expression in right tree:', right)
            if RANGE_VAR in right:
                pass

        # for key, value in right.items():
        #     print('{}: {}'.format(key, value))
        # print('RIGHT:', right)

        if JOIN_EXPR in joinExpr:
            pass

        return joinExpr


if __name__ == '__main__':
    # Query('''select person.id, avg(person.age) from person
    #     join employee on person.id = employee.id''')
    q = Query('''select person.id, avg(person.age) from person
        join employee on person.id = employee.id
        join manager on manager.emplId = employee.id''')
    # q2 = Query('select person.id, person.age from person;')
