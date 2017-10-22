from mypgparse import queryToJsonTree


class JoinOp:
    def __init__(self, leftTable, leftCol, rightTable, rightCol):
        self.leftTable = leftTable
        self.leftColumn = leftCol
        self.rightTable = rightTable
        self.rightColumn = rightCol


class JoinClause:
    def __init__(self, joinStr):
        self.joins = list(JoinOp('...'), JoinOp('...'))


class Query(object):
    def __init__(self, query):
        self.joinClause = JoinClause('a join b on a.id = b.id join c on c.id = b.id')
        self.tables = list("a", "b", "c")
        self.selectColumns = list("a.id", "b.id", "c.id")


