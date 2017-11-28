# Input to me is a list of MV objects. Each MV object should have name, string query, list of table/column pairs.
class MaterializedView:
    def __init__(self, view_name, select_str, tableSets):
        self.name = view_name
        self.selectStr = select_str
        self.tableCols = tableSets

    def __str__(self):
        return self.name + ' = ' + self.selectStr + ' with ' + str(self.tableCols)

# Disclaimer: only some functions tested
def get_test_queries(file_name):
  with open(file_name) as f:
    test_queries = f.read().splitlines()
  return test_queries
  
def modify_queries(test_queries):
  modified_queries = []
  for query in test_queries:
    editable_query = query
    tables_cols = parse_query(query)
    for (table,col) in tables_cols:
      if(is_in_mv(mvs,table,col)):
         editable_query.replace(table+'.'+col, mv.name+'.'+table+'.'+col)
    modified_queries.append(editable_query)
  return modified_queries

def is_in_mv(mvs,table,col):
  for mv in mvs:
    if mv.tableCols.contains((table,col)):
      return true
  return false

def parse_query(query):
  tables_cols = []
  for word in query.split(' '):
    parts = word.split('.')
    print(parts)
    if len(parts) == 2:
      tables_cols.append((parts[0],parts[1]))
  return tables_cols

def run_queries(queries):
  with database("testdb", "test", "test") as db:
    for query in queries:
      db.execute(query) # How are we doing timing?





queries = get_test_queries("testing_queries.txt")
print(queries)
#modified_queries = modify_queries(queries)
#print(modified_queries)
for query in queries:
    print(parse_query(query))
