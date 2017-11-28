# Input to me is a list of MV objects. Each MV object should have name, string query, list of table/column pairs.
import pickle

def run_testing(file_name, mvs):
  test_queries = get_test_queries(file_name)
  modified_queries(test_queries, mvs)
  run_queries(modified_queries)

# Disclaimer: only some functions tested
def get_test_queries(file_name):
  with open(file_name) as f:
    test_queries = f.read().splitlines()
  return test_queries
  
def modify_queries(test_queries, mvs):
  modified_queries = []
  for query in test_queries:
    editable_query = query
    tables_cols = parse_query(query)
    for (table,col) in tables_cols:
      if(is_in_mv(mvs,table,col)):
         editable_query.replace(table+'.'+col, mv.name+'.'+table+'.'+col)
    modified_queries.append(editable_query)
  return modified_queries

def is_in_mv(mvs, table, col):
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

def save_queries(queries):
  string_queries = []
  for query in queries:
    string_queries.append(query.toString())

run_testing("testing_queries.txt",pickle.load(open("mvs.pickle","rb")))
