import os
import sys
import time
import subprocess
from pgWrapper import *
from tqdm import *

# File names for query subsets.
old_person_term_queries = "small_test.psql"
new_person_term_queries = "small_test_mv.psql"
old_utterance = "utterance_old.psql"
new_utterance = "utterance_new.psql"



'''
Runs all queries in a file.
:param filename: string filename of query file.
:returns: The total excution time for those queries. 
'''
def runAll(filename):
    start_time = time.time()
    result = subprocess.check_output("psql -Upostgres -hdatabase -f " + filename, shell=True)
    end = time.time() - start_time
    return (end, result)

'''
Writes values to a file.
:param file: The open file object
:param val: The string result of running the query.
'''
def writeToFile(file, val):
    val = str(val[1])
    val = val.replace("\\n", "\n")
    file.write(val)

'''
Runs two query files, one that has modified queries with 
our new MVs and one without our MVs. The ouputs are stored
and tested against each other to check if the outputs are
equivalent. The process happens n number of times defined
by epochs. Total and average runtimes are display on screen
when the test hash finished.
:param epochs: The number of times to run the test.
:new_queries: The file name of the query file with MVs.
:old_queries: The file name of the query file without MVs.
'''
def runTest(epochs, new_queries, old_queries):
    mv_time = 0;
    no_mv_time  = 0;
    all_vals = list()
    mv_f = open("mv.out", "w")
    no_mv_f = open("no_mv.out", "w")

    print("\n\nStarting Test")
    print("\nCaching Data")
    runAll(new_queries)
    runAll(old_queries)

    print("\nRunning " + str(epochs) + " Tests\n")
    for i in tqdm(range(epochs)):
        if i % 2 == 0:
            mv = runAll(new_queries)
            no_mv = runAll(old_queries)
        else:
            no_mv = runAll(old_queries)
            mv = runAll(new_queries)

        all_vals.append(str(i) + ", " + str(mv[0]) + ", " + str(no_mv[0]))

        
        mv_time += mv[0]
        no_mv_time += no_mv[0]
        writeToFile(mv_f, mv)
        writeToFile(no_mv_f, no_mv)
        if mv[1] != no_mv[1]:
            raise ValueError("Error: Query results did not match")
    
    mv_f.close()
    no_mv_f.close()
    output_vals(all_vals)

    print("\n\nFinished\nTotal runtime with MVs: ", mv_time)
    print("Total runtime without MVs:    ", no_mv_time)
    print("Total runtime difference: ", no_mv_time - mv_time)
    print("\n\nAverage runtime with MVs: ", mv_time/epochs)
    print("Average runtime without MVs: ", no_mv_time/epochs)
    print("Average total runtime difference: ", (no_mv_time - mv_time)/epochs)

'''
Writes a list of times to a file to 
be used to analyze data and generate graphs.
:param all_vals: a list of strings formated
                 "epoch, time with MVs, time without MVs"
'''
def output_vals(all_vals):
    with open("result.csv", "w") as file:
        file.write("epoch, with mv, without mv\n")
        for val in all_vals:
            file.write(val + "\n") 


print("\n\nRunning Person_Term Test")
runTest(int(sys.argv[1]), new_person_term_queries, old_person_term_queries)