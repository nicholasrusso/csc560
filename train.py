# For each query
  # Add to counter for referenced tables - tables in Join clause or tables list?

# For each set of table with counters above threshold - set of tables?
  # Create MV
  # Create index
  # Add MV to our stored database model

from parser import Query

def create_mv(tables):
    table_name = '_'.join(tables) # what is this? pseudo code?
    data_query = "SELECT * FROM " + ','.join(tables)
    create_query = "CREATE MATERIALIZED VIEW " + table_name + " AS " + data_query
    # execute query
    # add MV to database model


def create_index(tables):
    create_query = "CREATE INDEX " + index_name + "ON " + table_name # index on column name?
    # execute query


def process_model(queryModel):
    tableCounts = {}
    for i in range(len(queryModel.tables)): # do we care
        if (queryModel[i] not in tableCounts):
            tableCounts[queryModel[i]] = 1
        else:
            curCount = tableCounts[queryModel[i]]
            tableCounts[queryModel[i]] = curCount + 1

    return tableCounts

