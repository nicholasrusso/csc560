/*
 * pythonInterface.c
 *
 *  Created on: Oct 17, 2017
 *      Author: brandon
 */

#include "Python.h"

#include "pg_query.h"
#include "pg_query_json.h"

char *do_parse_json(const char* query);
static PyObject *doParseJson_wrapper(PyObject *self, PyObject *args);

PyObject *doParseJson_wrapper(PyObject *self, PyObject *args) {
	char *query;
	char *jsonParseTree;
	PgQueryParseResult queryTree;
	PyObject *ret;

	// parse arguments
	if (!PyArg_ParseTuple(args, "s", &query)) {
		return NULL;
	}

	queryTree = pg_query_parse(query);

	// build the resulting string into a Python object.
	ret = PyUnicode_FromString(queryTree.parse_tree);
	pg_query_free_parse_result(queryTree);

	return ret;
}

static PyMethodDef myPGParseMethods[] = {
		{"queryToJsonTree", doParseJson_wrapper, METH_VARARGS, "Parse a PostgreSQL statement"},
		{NULL, NULL, 0, NULL}
};

static struct PyModuleDef myPgParseModule = {
   PyModuleDef_HEAD_INIT,
   "mypgparse",   /* name of module */
   NULL, /* module documentation, may be NULL */
   -1,       /* size of per-interpreter state of the module,
                or -1 if the module keeps state in global variables. */
   myPGParseMethods
};

PyObject *PyInit_mypgparse(void) {
	return PyModule_Create(&myPgParseModule);
}

int main(int argc, char **argv) {
	PgQueryParseResult result;

	result = pg_query_parse("select id, name from person join employee on person.id = employee.person.id;");

	printf("Query tree:\n%s\n", result.parse_tree);
	return 0;
}
