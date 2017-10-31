# I need list of MVs with the columns in them including what table each column is from
# A list of our Query objects should work. I think I only need the "selectColumns" parameter since it includes table names.

import timeit

# Read input file
with open('testing.txt') as f:
  test_queries = f.readlines()

# For each line
for query in test_queries:
  # Replace with our MV if appropriate
  # For each MV we've made
  #   For each column in query
  #     If that column isn't in MV 
  #       Break
  #     Else if last column in query
  #       Do replacement

print("Time elapsed: "+timeit.timeit(run_queries(queries))) #Not sure if this is correct


def run_queries(queries):
      for query in queries:
        #run
