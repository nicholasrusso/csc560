# For each query
  # Add to counter for referenced tables

# For each set of table with counters above threshold 
  # Create MV
  # Create index
  # Add MV to our stored database model


def create_mv(tables):
    table_name = '_'.join(tables)
    data_query = "SELECT * FROM " + ','.join(tables)
    create_query = "CREATE MATERIALIZED VIEW " + tale_name + " AS " + data_query
