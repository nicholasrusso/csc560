# Input to me is a list of MV objects. Each MV object should have name, string query, list of table/column pairs.
import pickle
from train import MaterializedView


def modify_queries(test_queries, mvs):
  modified_queries = []
# get list of the tables in the join
# see if an mv exactly matches that list of tables
# call tablename replacement tablename
  print("modify_queries")

  for query in test_queries:
    print(query.tables)
    for mv in mvs:
        if match_mv(mv, query.tables):
            #print("match")
            continue
  return modified_queries

def match_mv(mv, tables):
  for (table,col) in mv.tableCols:
    if table not in tables:
      return False
  return True

def is_in_mvs(mvs, table, col):
  for mv in mvs:
    if mv.tableCols.contains((table,col)):
      return true
  return false

def run_testing(test_queries, mvs):
    print("MVs");
    print(str(mvs[0]))
    print(str(mvs[1]))
    print(str(mvs[2]))
    print(str(mvs[3]))
    print("test_queries")
    print(test_queries[0])
    print(test_queries[0])
    print(test_queries[0])
    print(test_queries[0])
    modify_queries(test_queries, mvs)
#  run_queries(modified_queries)

def save_queries(queries):
  string_queries = []
  for query in queries:
    string_queries.append(query.toString())

run_testing(pickle.load(open("queries.pickle","rb")),pickle.load(open("MVs.p","rb")))

