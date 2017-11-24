import json

from mypgparse import queryToJsonTree

SELECT_STMT = 'SelectStmt'
FROM_CLAUSE = 'fromClause'
TARGET_LIST = 'targetList'
RES_TARGET = 'ResTarget'
VALUE = 'val'

RELATION_NAME = 'relname'
COLUMN_REF = 'ColumnRef'
FIELDS = 'fields'
JOIN_EXPR = 'JoinExpr'
FUNC_CALL = 'FuncCall'
FUNC_NAME = 'funcname'
FUNC_ARGS = 'args'
AGG_STAR = 'agg_star'
A_STAR = 'A_Star'

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

class FuncCall:
    def __init__(self, funcCallTree=None):
        # print('Function call:', funcCallTree)
        self.args = []
        self.funcName = None

        if funcCallTree is not None:
            if FUNC_NAME in funcCallTree and len(funcCallTree[FUNC_NAME]) > 0:
                self.funcName = funcCallTree[FUNC_NAME][0][STRING_TYPE][STR_TYPE]
            if FUNC_ARGS in funcCallTree and len(funcCallTree[FUNC_ARGS]) > 0:
                funcArgs = funcCallTree[FUNC_ARGS]

                for arg in funcArgs:
                    if COLUMN_REF in arg:
                        self.args.append(ColumnRef(arg[COLUMN_REF]))
            if AGG_STAR in funcCallTree and funcCallTree[AGG_STAR]:
                self.args.append('*')

    @staticmethod
    def create(funcName, args):
        func = FuncCall()
        func.funcName = funcName
        func.args = args
        return func

    def __str__(self):
        return '{}({})'.format(self.funcName, ', '.join([str(arg) for arg in self.args]))

    def __eq__(self, other):
        equal = False

        if other is not None and type(other) is FuncCall:
            equal = self.funcName == other.funcName \
                    and self.args is not None and other.args is not None \
                    and len(self.args) == len(other.args) \
                    and self.args == other.args

        return equal


class ColumnRef:
    def __init__(self, columnRefTree=None):
        if columnRefTree is not None:
            fieldTree = columnRefTree[FIELDS]
            fields = []
            hasAStar = False

            for field in fieldTree:
                if A_STAR in field:
                    hasAStar = True
                    fields.append('*')
                elif STRING_TYPE in field:
                    stringField = field[STRING_TYPE]
                    if STR_TYPE in stringField:
                        fields.append(stringField[STR_TYPE])
                    else:
                        print('Cannot handle ColumnRef field:', stringField)
            # fields = [field[STRING_TYPE][STR_TYPE] for field in fieldTree]
            if hasAStar:
                self.field = '*'
            else:
                self.field = '.'.join(fields)

            # Fields in "table.attribute" format
            if len(fields) == 2:
                self.table = fields[0]
            else:
                self.table = None
                # print('ColumnRef:', self.field)

    @staticmethod
    def create(field, table):
        col = ColumnRef()
        col.field = field
        col.table = table
        return col

    def __str__(self):
        return self.field

    def __eq__(self, other):
        equal = False

        if other is not None and type(other) is ColumnRef:
            equal = self.field == other.field and self.table == other.table

        return equal


class Expression:
    def __init__(self, exprTree):
        if COLUMN_REF in exprTree:
            column = exprTree[COLUMN_REF]
            # fields =
        # print('Expression:', exprTree)


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

    def __eq__(self, other):
        return type(other) is JoinOp and self.leftTable == other.leftTable \
               and self.leftColumn == other.leftColumn \
               and self.rightTable == other.rightTable \
               and self.rightColumn == other.rightColumn


class JoinClause:
    def __init__(self, joinOps):
        self.joins = joinOps

    def __eq__(self, other):
        return type(other) is JoinClause and self.joins == other.joins

    def __str__(self):
        return '\n'.join(str(joinOp) for joinOp in self.joins)


class Query(object):
    def __init__(self, query):
        if type(query) is str:
            print(query, '\n')
            parseTree = json.loads(queryToJsonTree(query))
        else:
            parseTree = query

        if type(parseTree) is list and len(parseTree) == 1:
            parseTree = parseTree[0]

        if SELECT_STMT not in parseTree:
            raise ValueError('Expected a select statement')

        self.parseTree = parseTree
        self.joinClause = None
        self.tables = set()
        self.selectColumns = []

        if SELECT_STMT in parseTree:
            self.parseSelectClause(parseTree[SELECT_STMT])
            # print('Selected Columns:', str(self.selectColumns))
        else:
            raise KeyError('Expected select query')

        self.parseFromClause(parseTree)
        # print('Tables:', self.tables)
        # print('Joins:', str(self.joinClause))

    def __eq__(self, other):
        return type(other) is Query and self.joinClause == other.joinClause \
               and self.tables == other.tables and self.selectColumns == other.selectColumns

    def parseNode(self, node):
        if FROM_CLAUSE in node:
            return self.parseFromClause(node[FROM_CLAUSE])
        elif JOIN_EXPR in node:
            return self.parseSingleJoinExpr(node[JOIN_EXPR])
        elif QUALIFIERS in node:
            return self.createJoinOp(node)
        elif RANGE_VAR in node:
            return self.parseRangeVar(node)

    def parseSelectClause(self, selectStmt):
        selectedCols = []
        if TARGET_LIST in selectStmt:
            targetList = selectStmt[TARGET_LIST]

            for target in targetList:
                if RES_TARGET in target:
                    targetValue = self._parseResTarget(target[RES_TARGET])

                    if targetValue is not None:
                        selectedCols.append(targetValue)

        self.selectColumns = [col for col in selectedCols]

    def _parseResTarget(self, resTarget):
        targetValue = None
        if VALUE in resTarget:
            val = resTarget[VALUE]

            if COLUMN_REF in val:
                targetValue = ColumnRef(val[COLUMN_REF])
            # TODO: Parse function calls
            elif FUNC_CALL in val:
                targetValue = FuncCall(val[FUNC_CALL])
        return targetValue

    def parseFromClause(self, parseTree):
        select = parseTree[SELECT_STMT]
        fromClause = select[FROM_CLAUSE]
        self.parseJoins(fromClause)

        if self.joinClause is None and len(fromClause) > 0:
            self.tables = {self.parseRangeVar(rangeVar) for rangeVar in fromClause
                           if RANGE_VAR in rangeVar}

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
    # Query('''select person.id, person.age, person.name from person
    #     join employee on person.id = employee.id''')
    # q = Query('''select Person.id, avg(Person.age) from Person
    #     join employee on Person.id = employee.id
    #     join manager on manager.emplId = employee.id''')
    # q = Query('''select Person.id, avg(Person.age) from Person
    #     join employee on Person.id = employee.id
    #     join manager on manager.emplId = employee.id
    #     join exec on exec.id = manager.execId''')
    # q2 = Query('select person.id, person.age from person;')
    # q = Query('select count(person.id) from person')
    q = Query('select count(*) from person')
