import json

from mypgparse import queryToJsonTree

SELECT_STMT = 'SelectStmt'
FROM_CLAUSE = 'fromClause'
WHERE_CLAUSE = 'whereClause'
GROUP_CLAUSE = 'groupClause'
TARGET_LIST = 'targetList'
RES_TARGET = 'ResTarget'
VALUE = 'val'

RELATION_NAME = 'relname'
COLUMN_REF = 'ColumnRef'
FIELDS = 'fields'
JOIN_EXPR = 'JoinExpr'
FUNC_CALL = 'FuncCall'
FUNC_NAME = 'funcname'
SINGLE_ARG = 'arg'
FUNC_ARGS = 'args'
AGG_STAR = 'agg_star'
A_STAR = 'A_Star'

A_CONST = 'A_Const'
INTEGER_TYPE = 'Integer'
INTEGER_VAL = 'ival'
NULL_TEST = 'NullTest'
NULL_TEST_TYPE = 'nulltesttype'
NULL_TEST_NOT_NULL = 1
NULL_TEST_IS_NULL = 0

RANGE_VAR = 'RangeVar'
LEFT_ARG = 'larg'
LEFT_EXPR = 'lexpr'
RIGHT_ARG = 'rarg'
RIGHT_EXPR = 'rexpr'
A_EXPR = 'A_Expr'
BOOL_EXPR = 'BoolExpr'
QUALIFIERS = 'quals'
NAME = 'name'
STRING_TYPE = 'String'
STR_TYPE = 'str'

LIKE = '~~'


# NOTE: queryToJsonTree seems to lowercase all references (columns, tables, etc)

class FuncCall:
    def __init__(self, funcCallTree=None):
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
                self.args.append(ColumnRef.create('*', None))

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


class Constant:
    def __init__(self, value, typ):
        if typ == STRING_TYPE:
            self.value = '\'{}\''.format(str(value))
        else:
            self.value = value
        self.type = typ

    def __str__(self):
        # return '<Constant: val={}, type={}>'.format(str(self.value), self.type)
        return str(self.value)

    def __eq__(self, other):
        return type(other) is Constant and self.value == other.value \
               and self.type == other.type


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
            if hasAStar:
                self.field = '*'
            else:
                self.field = '.'.join(fields)

            # Fields in "table.attribute" format
            if len(fields) == 2:
                self.table = fields[0]
            else:
                self.table = None

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


class NullTest:
    def __init__(self, arg, isNull):
        self.arg = arg
        self.isNull = isNull

    def __eq__(self, other):
        return type(other) is NullTest and \
               self.arg == other.arg and self.isNull == other.isNull

    def __str__(self):
        return '{} is {}'.format(str(self.arg),
                                 'null' if self.isNull
                                 else 'not null')


class BinaryOp:
    def __init__(self, leftExpr, rightExpr, operator):
        self.leftColumn = leftExpr
        self.rightColumn = rightExpr
        self.operator = operator

    def __eq__(self, other):
        return isinstance(other, BinaryOp) \
               and self.leftColumn == other.leftColumn \
               and self.rightColumn == other.rightColumn

    def __str__(self):
        if self.operator == LIKE:
            operator = 'like'
        else:
            operator = self.operator
        if self.rightColumn is not None and type(self.rightColumn) is ColumnRef \
                and self.rightColumn.field != AGG_STAR and self.rightColumn.table is None:
            rightColumn = "'{}'".format(self.rightColumn)
        else:
            rightColumn = self.rightColumn

        return '{} {} {}'.format(str(self.leftColumn)
                                 if self.leftColumn is not None
                                 else 'NIL',
                                 str(operator)
                                 if operator is not None
                                 else 'NIL',
                                 str(rightColumn)
                                 if rightColumn is not None
                                 else 'NIL')


class JoinOp(BinaryOp):
    def __init__(self, leftTable, leftExpr, rightTable, rightExpr, operator):
        BinaryOp.__init__(self, leftExpr, rightExpr, operator)
        self.leftTable = leftTable
        self.rightTable = rightTable

    def __str__(self):
        return '{} join {} on {} {} {}'.format(
            self.leftTable, self.rightTable, self.leftColumn,
            self.operator, self.rightColumn
        )

    def __eq__(self, other):
        return type(other) is JoinOp and BinaryOp.__eq__(self, other) \
               and self.leftTable == other.leftTable \
               and self.rightTable == other.rightTable

    @staticmethod
    def fromBinOp(binOp, leftTable, rightTable):
        join = None
        if type(binOp) is BinaryOp:
            join = JoinOp(leftTable, binOp.leftExpr,
                          rightTable, binOp.rightExpr, binOp.operator)

        return join


class JoinClause:
    def __init__(self, joinOps):
        self.joins = joinOps

    def __eq__(self, other):
        return type(other) is JoinClause and self.joins == other.joins

    def __str__(self):
        return ' '.join(str(joinOp) for joinOp in self.joins)


class WhereClause:
    '''
    :param whereStatements list of BinaryOp and\or NullTest
    '''
    def __init__(self, whereStatements):
        self.whereStatements = whereStatements

    def __eq__(self, other):
        return type(other) is WhereClause and self.whereStatements == other.whereStatements

    # NOTE: Only works with boolean 'and' expressions
    def __str__(self):
        return 'where {}'.format(' and '.join(str(whereStmt) for whereStmt in self.whereStatements))


class GroupClause:
    def __init__(self, groupStatements):
        self.groupStatements = groupStatements

    def __eq__(self, other):
        return type(other) is GroupClause and self.groupStatements == other.groupStatements

    def __str__(self):
        return 'group by {}'.format(', '.join([str(stmt) for stmt in self.groupStatements]))


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
        self.tables = set()
        self.selectColumns = []
        self.joinClause = None
        self.whereClause = None
        self.groupClause = None

        if SELECT_STMT in parseTree:
            select = parseTree[SELECT_STMT]
            self.parseSelectClause(select)
            if WHERE_CLAUSE in select:
                self.whereClause = self.parseWhereClause(select[WHERE_CLAUSE])
            if GROUP_CLAUSE in select:
                self.groupClause = GroupClause([self.parseNode(groupBy)
                                                for groupBy in select[GROUP_CLAUSE]])
        else:
            raise KeyError('Expected select query')

        self.parseFromClause(parseTree)

    def __eq__(self, other):
        return type(other) is Query and self.joinClause == other.joinClause \
               and self.tables == other.tables and self.selectColumns == other.selectColumns

    def __str__(self):
        queryStr = 'select {} from '.format(', '.join([str(col) for col in self.selectColumns]))

        if self.joinClause is not None:
            queryStr += str(self.joinClause)
        else:
            queryStr += ', '.join(self.tables)
        if self.whereClause is not None:
            queryStr += ' ' + str(self.whereClause)
        if self.groupClause is not None:
            queryStr += ' ' + str(self.groupClause)

        return queryStr + ';'

    def parseNode(self, node):
        if LEFT_EXPR in node and RIGHT_EXPR in node:
            left = self.parseNode(node[LEFT_EXPR])
            right = self.parseNode(node[RIGHT_EXPR])
            return left, right
        if FROM_CLAUSE in node:
            return self.parseFromClause(node[FROM_CLAUSE])
        elif JOIN_EXPR in node:
            return self.parseSingleJoinExpr(node[JOIN_EXPR])
        elif QUALIFIERS in node:
            return self.createJoinOp(node)
        elif RANGE_VAR in node:
            return self.parseRangeVar(node)
        elif A_EXPR in node:
            return self.parseAExpr(node[A_EXPR])
        elif BOOL_EXPR in node:
            return self.parseNode(node[BOOL_EXPR])
        elif FUNC_ARGS in node:
            return [self.parseNode(arg) for arg in node[FUNC_ARGS]]
        elif A_CONST in node:
            return self.parseAConst(node[A_CONST])
        elif NULL_TEST in node:
            return self.parseNullTest(node[NULL_TEST])
        elif COLUMN_REF in node:
            return ColumnRef(node[COLUMN_REF])
        elif FUNC_CALL in node:
            return FuncCall(node[FUNC_CALL])

        raise ValueError('Failed to parseNode:' + str(node))

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

    def parseWhereClause(self, whereClauseTree):
        whereClause = self.parseNode(whereClauseTree)

        if type(whereClause) is not list:
            whereClause = [whereClause]

        return WhereClause(whereClause)

    def _parseResTarget(self, resTarget):
        targetValue = None
        if VALUE in resTarget:
            val = resTarget[VALUE]

            if COLUMN_REF in val:
                targetValue = ColumnRef(val[COLUMN_REF])
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
        right = joinExpr[RIGHT_ARG]
        joins = []

        if QUALIFIERS in joinExpr:
            joins.extend(self.createJoinOp(joinExpr))
        else:
            if JOIN_EXPR in left:
                leftJoins = self.parseSingleJoinExpr(left)
                joins.extend(leftJoins)

            if JOIN_EXPR in right:
                joins.extend(self.parseSingleJoinExpr(right))
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

    def parseBoolExpr(self, boolExpr):
        boolExprArgs = self.parseNode(boolExpr)
        return boolExprArgs

    def parseAExpr(self, aExprTree):
        operator = None
        left = None
        right = None

        if NAME in aExprTree:
            operator = aExprTree[NAME]
            if type(operator) is list:
                operator = operator[0]
            if STRING_TYPE in operator:
                operator = operator[STRING_TYPE]
                if STR_TYPE in operator:
                    operator = operator[STR_TYPE]
        if LEFT_EXPR in aExprTree and RIGHT_EXPR in aExprTree:
            exprs = self.parseNode(aExprTree)
            if len(exprs) == 2:
                left, right = exprs
            else:
                raise ValueError('Failed to parse A_Expr')

        return BinaryOp(left, right, operator)

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
            leftArg = joinExprTree[LEFT_ARG]
            if JOIN_EXPR in leftArg:
                leftJoins = self.parseSingleJoinExpr(leftArg)
                joinOps.extend(leftJoins)
            else:
                leftTable = joinExprTree[LEFT_ARG][RANGE_VAR][RELATION_NAME]
        if RIGHT_ARG in joinExprTree:
            rightArg = joinExprTree[RIGHT_ARG]

            if JOIN_EXPR in rightArg:
                rightJoins = self.parseSingleJoinExpr(rightArg)
            else:
                rightTable = joinExprTree[RIGHT_ARG][RANGE_VAR][RELATION_NAME]

        leftCol, rightCol = self.parseNode(join)
        if leftCol.table is not None:
            leftTable = leftCol.table
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

    def parseAConst(self, constExpr):
        constValue = None

        if VALUE in constExpr:
            val = constExpr[VALUE]

            if STRING_TYPE in val:
                stringType = val[STRING_TYPE]
                if STR_TYPE in stringType:
                    constValue = Constant(stringType[STR_TYPE], STRING_TYPE)
                else:
                    raise ValueError('Couldn\'t parse string value from string type in:',
                                     stringType)
            elif INTEGER_TYPE in val:
                integerType = val[INTEGER_TYPE]
                if INTEGER_VAL in integerType:
                    constValue = Constant(int(integerType[INTEGER_VAL]), INTEGER_TYPE)
                else:
                    raise ValueError('Couldn\'t parse integer value from integer type in:',
                                     integerType)

        return constValue

    def parseNullTest(self, nullTestExpr):
        nullTest = None

        if SINGLE_ARG in nullTestExpr:
            arg = self.parseNode(nullTestExpr[SINGLE_ARG])
        else:
            raise ValueError('Couldn\t find argument in NullTest:', nullTestExpr)

        if NULL_TEST_TYPE in nullTestExpr:
            nullTestType = int(nullTestExpr[NULL_TEST_TYPE])
            nullTest = NullTest(arg, nullTestType == NULL_TEST_IS_NULL)

        return nullTest
