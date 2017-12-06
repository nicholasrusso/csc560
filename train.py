# For each query
  # Add to counter for referenced tables

# For each set of table with counters above threshold
  # Create MV
  # Create index
  # Add MV to our stored database model

import pickle
#from parseQueryFile import *
from pgWrapper import *

class MaterializedView:
    def __init__(self, view_name, select_str, tableSets):
        self.name = view_name
        self.selectStr = select_str
        self.tableCols = tableSets

    def __str__(self):
        return self.name + ' = ' + self.selectStr + ' with ' + str(self.tableCols)



# given a query model, for every set of tables (being joined), add to counter dict for tables being joined
def process_model(queryModel, tableCounts):
    # queryModel.joinClause.joins = list of JoinOps(leftTable, leftCol, rightTable, rightCol, joinOperator)
    if queryModel.joinClause is not None:
        joins = queryModel.joinClause.joins

        for i in range(len(queryModel.joinClause.joins)):
            leftTable = joins[i].leftTable
            rightTable = joins[i].rightTable
            leftCol = str(joins[i].leftColumn).split(".")[1]
            rightCol = joins[i].rightColumn.split(".")[1]
            joinOper = joins[i].operator

            if ((leftTable, leftCol), (rightTable, rightCol), joinOper) not in tableCounts:
                tableCounts[((leftTable, leftCol), (rightTable, rightCol), joinOper)] = 1
            else:
                curCount = tableCounts[((leftTable, leftCol), (rightTable, rightCol), joinOper)]
                tableCounts[((leftTable, leftCol), (rightTable, rightCol), joinOper)] = curCount + 1

        #print(tableCounts)



#tableCounts is dict = {((leftTable, leftCol), (rightTable, rightCol), joinOper) -> count}
def createViews(tableCounts, threshold, db):
    MVs = []
    indexes = {}

    # tableSet = ((leftTable, leftCol), (rightTable, rightCol), joinOper)
    for tableSet, count in tableCounts.items():
        if count > threshold:
            tables = list(tableSet[:-1] ) # slices off the joinOper
            joinOper = tableSet[-1]

            MVs.append(create_mv(tables, joinOper, db))

            for table, col in tables:
                if (table, col) not in indexes:
                    create_index(table, col, db)
                    indexes[(table, col)] = 1

    return MVs



# tableSets = [(leftTable, leftCol), (rightTable, rightCol)]
def create_mv(tableSets, joinOper, db):
    tables = []
    for table, col in tableSets:
        tables.append(table)

    view_name = '_'.join(tables)

    #'select * from person join employee on person.id = employee.id'
    select_str = "SELECT * FROM " + ' JOIN '.join(tables) #
    data_query = select_str + " on " + '.'.join(list(tableSets[0])) + joinOper + '.'.join(list(tableSets[1]))

    create_query = "CREATE MATERIALIZED VIEW IF NOT EXISTS " + view_name + " AS " + data_query

    mv = MaterializedView(view_name, select_str, tableSets)
    print(str(mv))

    db.execute(create_query)

    return mv



# should indexes be made on each table in the set of tables being joined?
def create_index(table, column, db):
    index_name = table + "_" + column + "_index"
    index_query = "CREATE INDEX IF NOT EXISTS " + index_name + " ON " + table + "(" + column + ")"

    db.execute(index_query)



if __name__ == '__main__':
    #if len(argv) >= 2:
    #    queryFile = argv[1]
    #    queries = parseFile(queryFile)
    #    pickle.dump(queries, open("newParsedQueries.p", "wb"))
    #    print('Successfully parsed {} queries'.format(len(queries)))

        file = open("newParsedQueries.p", "rb")
        queries = pickle.load(file)
        file.close()

        tableCounts = {}

        for i in range(len(queries)):
            process_model(queries[i], tableCounts)

        #MVs = createViews(tableCounts, 1)

        #pickle.dump(MVs, open("MVs.p", "wb"))

        with pgWrapper("test", "postgres", "", "database") as db:
            MVs = createViews(tableCounts, 1, db)
            pickle.dump(MVs, open("MVs.p", "wb"))