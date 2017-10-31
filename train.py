# For each query
  # Add to counter for referenced tables

# For each set of table with counters above threshold
  # Create MV
  # Create index
  # Add MV to our stored database model

# Tester needs MV name, columns, tables

from parser import Query

class MaterializedView:
    def _init_(self, queryStr):
        self.name =
        self.selectStr =
        self.columns =
        self.tables =


def create_mv(tables):
    view_name = '_'.join(tables)
    data_query = "SELECT * FROM " + ','.join(tables)
    create_query = "CREATE MATERIALIZED VIEW " + view_name + " AS " + data_query
    # execute query
    # add MV to database model & output for tester?


# should indexes be made on each table in the set of tables being joined?
def create_index(table):
    index_name = table + '_index'
    create_query = "CREATE INDEX " + index_name + "ON " + table # index on column name?
    # execute query


# given a query model, for every set of tables (being joined), add to counter dict for tables being joined
def process_model(queryModel):
    # queryModel.joinClause.joins = list of JoinOps(leftTable, leftCol, rightTable, rightCol, joinOperator)
    joins = queryModel.joinClause.joins
    tableCounts = {}

    for i in range(len(queryModel.joinClause.joins)):
        leftTable = joins[i].leftTable
        rightTable = joins[i].rightTable

        if (leftTable, rightTable) not in tableCounts:
            tableCounts[(leftTable, rightTable)] = 1
        else:
            curCount = tableCounts[(leftTable, rightTable)]
            tableCounts[(leftTable, rightTable)] = curCount + 1

    return tableCounts


def createViews(tableCounts, threshold):
    for tableSet, count in tableCounts.items():
        if count > threshold:
            create_mv(list(tableSet)) # convert to list for str.join()
            for table in tableSet:
                create_index(table)
