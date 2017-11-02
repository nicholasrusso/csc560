import unittest
from parser import *


class ParserTests(unittest.TestCase):
    def testSimpleQuery(self):
        query = Query('select person.id, person.age from person;')
        self.assertIsNone(query.joinClause)
        expectedSelectCols = ['person.id', 'person.age']
        self.assertEqual(query.selectColumns, expectedSelectCols)
        expectedTables = {'person'}
        self.assertEqual(query.tables, expectedTables)

    def testSingleJoin(self):
        query = Query('''select person.id, person.age, person.name from person
            join employee on person.id = employee.id''')
        expectedJoins = JoinClause([JoinOp('person', 'person.id', 'employee', 'employee.id', '=')])
        self.assertEqual(query.joinClause, expectedJoins)
        expectedSelectCols = ['person.id', 'person.age', 'person.name']
        self.assertEqual(query.selectColumns, expectedSelectCols)
        expectedTables = {'person', 'employee'}
        self.assertEqual(query.tables, expectedTables)

    def testDoubleJoin(self):
        query = Query('''select person.id, avg(person.age) from person
            join employee on person.id = employee.id
            join manager on manager.emplid = employee.id''')
        expectedJoins = JoinClause([JoinOp('person', 'person.id', 'employee', 'employee.id', '='),
                                    JoinOp('manager', 'manager.emplid', 'employee', 'employee.id', '=')])
        self.assertEqual(query.joinClause, expectedJoins)
        # TODO: Fix when function parsing is added
        expectedSelectCols = ['person.id']
        self.assertEqual(query.selectColumns, expectedSelectCols)
        expectedTables = {'person', 'employee', 'manager'}
        self.assertEqual(query.tables, expectedTables)

    def testTripleJoin(self):
        query = Query('''select person.id, avg(person.age) from person
            join employee on person.id = employee.id
            join manager on manager.emplid = employee.id
            join exec on exec.id = manager.execid''')
        expectedJoins = JoinClause([JoinOp('person', 'person.id', 'employee', 'employee.id', '='),
                                    JoinOp('manager', 'manager.emplid', 'employee', 'employee.id', '='),
                                    JoinOp('exec', 'exec.id', 'manager', 'manager.execid', '=')])
        self.assertEqual(query.joinClause, expectedJoins)
        # TODO: Fix when function parsing added
        expectedSelectCols = ['person.id']
        self.assertEqual(query.selectColumns, expectedSelectCols)
        expectedTables = {'person', 'employee', 'manager', 'exec'}
        self.assertEqual(query.tables, expectedTables)


if __name__ == '__main__':
    unittest.main()
