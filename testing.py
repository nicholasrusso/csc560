# Input to me is a list of MV objects. Each MV object should have name, string query, list of table/column pairs.
import pickle
from train import MaterializedView
from copy import deepcopy

def modify_queries(test_queries, mvs):
  modified_queries = []
# get list of the tables in the join
# see if an mv exactly matches that list of tables
# call tablename replacement tablename
  #print("modify_queries")

  for query in test_queries:
    editable_query = deepcopy(query)
  #  print(query.tables)
    for mv in mvs:
        if match_mv(mv, query.tables):
          for table in query.tables:
            editable_query.replaceTable(table, mv.name)
        modified_queries.append(editable_query) 
  return modified_queries

def match_mv(mv, tables):
  if len(mv.tableCols) != len(tables):
    return False
  for (table,col) in mv.tableCols:
    if table not in tables:
      return False
 # print("mv # tables: "+str(len(mv.tableCols))+" query # tables: "+str(len(tables)))
 # print("true: "+table+" in "+str(mv.tableCols)+" rename as "+mv.name)
  return True

def run_testing(test_queries, mvs):
    save_queries(modify_queries(test_queries, mvs))

def save_queries(queries):
  string_queries = []
  for query in queries:
    string_queries.append(str(query))
  with open("modified_queries.txt","w") as f:
    f.write('\n'.join(string_queries))

run_testing(pickle.load(open("queries.pickle","rb")),pickle.load(open("MVs.p","rb")))

