import timeit

# Read input file
with open('testing.txt') as f:
  test_queries = f.readlines()

# For each line
for query in test_queries:
  # Replace with our MV if appropriate

print("Time elapsed: "+timeit.timeit(run_queries(queries))) #Not sure if this is correct


def run_queries(queries):
      for query in queries:
        #run
