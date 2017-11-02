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

LIKE = '~~'


# NOTE: queryToJsonTree seems to lowercase all references (columns, tables, etc)

class ColumnRef:
    def __init__(self, columnRefTree):
        fieldTree = columnRefTree[FIELDS]
        fields = [field[STRING_TYPE][STR_TYPE] for field in fieldTree]
        self.field = '.'.join(fields)

        # Fields in "table.attribute" format
        if len(fields) == 2:
            self.table = fields[0]
        else:
            self.table = None
            # print('ColumnRef:', self.field)


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

    def __str__(self):
        return '{} join {} on {} {} {}'.format(
            self.leftTable, self.rightTable, self.leftColumn,
            self.joinOperator, self.rightColumn
        )


class JoinClause:
    def __init__(self, joinOps):
        self.joins = joinOps

    def __str__(self):
        return '\n'.join(str(joinOp) for joinOp in self.joins)


class Query(object):
    def __init__(self, query):
        print(query, '\n')
        parseTree = json.loads(queryToJsonTree(query))
        if type(parseTree) is list and len(parseTree) == 1:
            parseTree = parseTree[0]

        if SELECT_STMT not in parseTree:
            raise ValueError('Expected a select statement')

        self.parseTree = parseTree
        self.joinClause = None
        self.tables = set()
        self.selectColumns = ["a.id", "b.id", "c.id"]

        self.parseFromClause(parseTree)
        print('Tables:', self.tables)
        print('Joins:', str(self.joinClause))

    def parseNode(self, node):
        if FROM_CLAUSE in node:
            return self.parseFromClause(node[FROM_CLAUSE])
        elif JOIN_EXPR in node:
            return self.parseSingleJoinExpr(node[JOIN_EXPR])
        elif QUALIFIERS in node:
            return self.createJoinOp(node)
        elif RANGE_VAR in node:
            return self.parseRangeVar(node)

    def parseFromClause(self, parseTree):
        select = parseTree[SELECT_STMT]
        fromClause = select[FROM_CLAUSE]
        self.parseJoins(fromClause)

    def parseJoins(self, fromClause):
        joins = []
        for clause in fromClause:
            if JOIN_EXPR in clause:
                joinExpr = clause[JOIN_EXPR]
                joins.extend(self.parseJoinExprs(joinExpr))

        if len(joins) > 0:
            self.joinClause = JoinClause(joins)
            for join in joins:
                self.tables.add(join.leftTable)
                self.tables.add(join.rightTable)

    def parseJoinExprs(self, joinExpr):
        left = joinExpr[LEFT_ARG]
        # print('LEFT:', left)
        right = joinExpr[RIGHT_ARG]
        # print('RIGHT:', right)
        joins = []

        if QUALIFIERS in joinExpr:
            # print('Top level join:', str(joinExpr[QUALIFIERS]))
            joins.extend(self.createJoinOp(joinExpr))
            # print('Top-level JoinOp:', topLevelJoin)
        else:
            if JOIN_EXPR in left:
                leftJoins = self.parseSingleJoinExpr(left)
                joins.extend(leftJoins)
                # print('Left join:', [str(leftJoin) for leftJoin in leftJoins])

            if JOIN_EXPR in right:
                joins.extend(self.parseSingleJoinExpr(right))
                # print('Right join:', str(rightJoins))
            elif RANGE_VAR in right:
                # TODO: Do we need this case?
                rightTable = self.parseRangeVar(right)

        return joins

    def parseSingleJoinExpr(self, joinExpr):
        if JOIN_EXPR in joinExpr:
            join = joinExpr[JOIN_EXPR]
        else:
            join = joinExpr
        if QUALIFIERS in join:
            joinExprs = self.createJoinOp(join)
        else:
            joinExprs = self.parseJoinExprs(join)

        return joinExprs

    def parseRangeVar(self, rangeVarExpr):
        rangeVar = rangeVarExpr[RANGE_VAR]
        return rangeVar[RELATION_NAME]

    def createJoinOp(self, joinExprTree):
        join = joinExprTree[QUALIFIERS][A_EXPR]
        operator = join[NAME]
        leftTable = None
        rightTable = None
        leftJoins = None
        rightJoins = None
        joinOps = []

        if type(operator) is list:
            operator = operator[0]

        operator = operator[STRING_TYPE][STR_TYPE]
        if LEFT_ARG in joinExprTree:
            # print('JoinExprTree[LEFT_ARG]:', joinExprTree[LEFT_ARG])
            leftArg = joinExprTree[LEFT_ARG]
            if JOIN_EXPR in leftArg:
                leftJoins = self.parseSingleJoinExpr(leftArg)
                joinOps.extend(leftJoins)
                # print('LEFT_JOIN:', [str(leftJoin) for leftJoin in leftJoins])
            else:
                leftTable = joinExprTree[LEFT_ARG][RANGE_VAR][RELATION_NAME]
        if RIGHT_ARG in joinExprTree:
            rightArg = joinExprTree[RIGHT_ARG]
            # print('JoinExprTree[RIGHT_ARG]:', rightArg)

            if JOIN_EXPR in rightArg:
                rightJoins = self.parseSingleJoinExpr(rightArg)
                # print('RIGHT_JOIN:', str(rightJoins))
            else:
                rightTable = joinExprTree[RIGHT_ARG][RANGE_VAR][RELATION_NAME]

        leftCol = None
        if LEFT_EXPR in join:
            leftExpr = join[LEFT_EXPR]
            if COLUMN_REF in leftExpr:
                leftCol = ColumnRef(leftExpr[COLUMN_REF])
                if leftCol.table is not None:
                    leftTable = leftCol.table

        rightCol = None
        if RIGHT_EXPR in join:
            rightExpr = join[RIGHT_EXPR]
            if COLUMN_REF in rightExpr:
                rightCol = ColumnRef(rightExpr[COLUMN_REF])
                if rightCol.table is not None:
                    rightTable = rightCol.table

        if leftTable is not None and rightTable is not None \
                and operator is not None and leftCol is not None \
                and rightCol is not None:
            joinOps.append(JoinOp(leftTable, leftCol.field,
                                  rightTable, rightCol.field, operator))
        if rightJoins is not None:
            joinOps.extend(rightJoins)
        return joinOps


if __name__ == '__main__':
    Query('''select person.id, avg(person.age) from person
        join employee on person.id = employee.id''')
    # q = Query('''select Person.id, avg(Person.age) from Person
    #     join employee on Person.id = employee.id
    #     join manager on manager.emplId = employee.id''')
    # q = Query('''select Person.id, avg(Person.age) from Person
    #     join employee on Person.id = employee.id
    #     join manager on manager.emplId = employee.id
    #     join exec on exec.id = manager.execId''')
    # q2 = Query('select person.id, person.age from person;')
