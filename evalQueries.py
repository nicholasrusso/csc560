import os
import sys
import time
import subprocess
from pgWrapper import *
from tqdm import *
import matplotlib.pylab as plt

dir = "/Users/nicholasrusso/Desktop/grad/560/project/csc560/"
old_person_term_queries = "small_test.psql"
new_person_term_queries = "small_test_mv.psql"
old_utterance = "utterance_old.psql"
new_utterance = "utterance_new.psql"


def runAll(filename):
    start_time = time.time()
    result = subprocess.check_output("psql -Upostgres -f " + filename, shell=True)
    end = time.time() - start_time
    return (end, result)

def writeToFile(file, val):
    val = str(val[1])
    for line in val.split("\\n"):
        file.write(line)

def runTest(epochs, new_queries, old_queries):
    mv_time = 0;
    no_mv_time  = 0;
    all_vals = list()
    mv_f = open("mv.out", "w")
    no_mv_f = open("no_mv.out", "w")
    print("Starting Test\nCaching Data")
    runAll(dir + new_queries)
    runAll(dir + old_queries)

    print("\nRunning " + str(epochs) + " Tests\n")
    for i in tqdm(range(epochs)):
        if i % 2 == 0:
            mv = runAll(dir + new_queries)
            no_mv = runAll(dir + old_queries)
        else:
            no_mv = runAll(dir + old_queries)
            mv = runAll(dir + new_queries)

        all_vals.append(str(i) + ", " + str(mv[0]) + ", " + str(no_mv[0]))

        if mv[1] != no_mv[1]:
            raise ValueError("Error: Query results did not match")
        mv_time += mv[0]
        no_mv_time += no_mv[0]
        writeToFile(mv_f, mv)
        writeToFile(no_mv_f, no_mv)
    
    mv_f.close()
    no_mv_f.close()
    output_vals(all_vals)

    print("\nFinished\nTotal runtime with MVs: ", mv_time)
    print("Total runtime without MVs:    ", no_mv_time)
    print("Total runtime difference: ", no_mv_time - mv_time)
    print("Average runtime with MVs: ", mv_time/epochs)
    print("Average runtime without MVs: ", no_mv_time/epochs)
    print("Total runtime difference: ", (no_mv_time - mv_time)/epochs)

def output_vals(all_vals):
    with open("result.csv", "w") as file:
        file.write("epoch, with mv, without mv\n")
        for val in all_vals:
            file.write(val + "\n") 


#runTest(int(sys.argv[1]), new_utterance, old_utterance)
runTest(int(sys.argv[1]), new_person_term_queries, old_person_term_queries)