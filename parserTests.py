import unittest
from parser import *


class ParserTests(unittest.TestCase):
    def testSimpleQuery(self):
        query = Query('select person.id, person.age from person;')
        self.assertIsNone(query.joinClause)
        expectedSelectCols = [ColumnRef.create('person.id', 'person'),
                              ColumnRef.create('person.age', 'person')]
        # expectedSelectCols = ['person.id', 'person.age']
        self.assertEqual(query.selectColumns, expectedSelectCols)
        expectedTables = {'person'}
        self.assertEqual(query.tables, expectedTables)

    def selectAStarQuery(self):
        query = Query('select * from person')
        self.assertIsNone(query.joinClause)
        expectedSelectCols = [ColumnRef.create('*', None)]
        self.assertEqual(query.selectColumns, expectedSelectCols)
        expectedTables = {'person'}
        self.assertEqual(query.tables, expectedTables)

    def testSingleJoin(self):
        query = Query('''select person.id, person.age, person.name from person
            join employee on person.id = employee.id''')
        expectedJoins = JoinClause([JoinOp('person', 'person.id', 'employee', 'employee.id', '=')])
        self.assertEqual(query.joinClause, expectedJoins)
        expectedSelectCols = [ColumnRef.create('person.id', 'person'),
                              ColumnRef.create('person.age', 'person'),
                              ColumnRef.create('person.name', 'person')]
        # expectedSelectCols = ['person.id', 'person.age', 'person.name']
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
        expectedSelectCols = [ColumnRef.create('person.id', 'person'),
                              FuncCall.create('avg', [ColumnRef.create('person.age', 'person')])]
        # expectedSelectCols = ['person.id']
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
        firstSelectCol = ColumnRef.create('person.id', 'person')
        secondSelectCol = FuncCall.create('avg', [ColumnRef.create('person.age', 'person')])
        expectedSelectCols = [firstSelectCol, secondSelectCol]
        # expectedSelectCols = ['person.id']
        self.assertEqual(query.selectColumns, expectedSelectCols)
        expectedTables = {'person', 'employee', 'manager', 'exec'}
        self.assertEqual(query.tables, expectedTables)

    def testFunc(self):
        query = Query('''select count(*) from person''')
        expectedSelectCols = [FuncCall.create('count', ['*'])]
        self.assertEqual(query.selectColumns, expectedSelectCols)
        self.assertIsNone(query.joinClause)
        expectedTables = {'person'}
        self.assertEqual(query.tables, expectedTables)

    def testSimpleWhereClause(self):
        query = Query('''select * from utterance, billdiscussion, bill, hearing, person
                        where utterance.did = billdiscussion.did
                        and billdiscussion.bid = bill.bid
                        and billdiscussion.hid = hearing.hid
                        and utterance.pid = person.pid;''')

    def testWhereClauseLike(self):
        query = Query('''select * from bill where bill.status like "%et%";''')


if __name__ == '__main__':
    unittest.main()
