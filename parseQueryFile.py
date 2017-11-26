from sys import argv
from json import loads

from mypgparse import queryToJsonTree
from parser import *


def parseFile(fileName):
    queries = []

    try:
        with open(fileName, 'r') as file:
            text = file.read()
            queryTrees = loads(queryToJsonTree(text))
            for queryTree in queryTrees:
                try:
                    queries.append(Query(queryTree))
                except:
                    print('Failed to parse query:', queryTree)
    except IOError:
        print('Failed to read given query file')

    return queries


if __name__ == '__main__':
    if len(argv) >= 2:
        queryFile = argv[1]
        queries = parseFile(queryFile)
        print('Successfully parsed {} queries'.format(len(queries)))
