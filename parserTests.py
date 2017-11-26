import unittest
from parser import *


class ParserTests(unittest.TestCase):
    def testSimpleQuery(self):
        query = Query('select person.id, person.age from person;')
        self.assertIsNone(query.joinClause)
        expectedSelectCols = [ColumnRef.create('person.id', 'person'),
                              ColumnRef.create('person.age', 'person')]
        self.assertEqual(query.selectColumns, expectedSelectCols)
        expectedTables = {'person'}
        self.assertEqual(query.tables, expectedTables)
        self.assertIsNone(query.groupClause)
        self.assertIsNone(query.whereClause)

    def selectAStarQuery(self):
        query = Query('select * from person')
        self.assertIsNone(query.joinClause)
        expectedSelectCols = [ColumnRef.create('*', None)]
        self.assertEqual(query.selectColumns, expectedSelectCols)
        expectedTables = {'person'}
        self.assertEqual(query.tables, expectedTables)
        self.assertIsNone(query.groupClause)
        self.assertIsNone(query.whereClause)

    def testSingleJoin(self):
        query = Query('''select person.id, person.age, person.name from person
            join employee on person.id = employee.id''')
        expectedJoins = JoinClause([JoinOp('person', 'person.id', 'employee', 'employee.id', '=')])
        self.assertEqual(query.joinClause, expectedJoins)
        expectedSelectCols = [ColumnRef.create('person.id', 'person'),
                              ColumnRef.create('person.age', 'person'),
                              ColumnRef.create('person.name', 'person')]
        self.assertEqual(query.selectColumns, expectedSelectCols)
        expectedTables = {'person', 'employee'}
        self.assertEqual(query.tables, expectedTables)
        self.assertIsNone(query.groupClause)
        self.assertIsNone(query.whereClause)

    def testDoubleJoin(self):
        query = Query('''select person.id, avg(person.age) from person
            join employee on person.id = employee.id
            join manager on manager.emplid = employee.id''')
        expectedJoins = JoinClause([JoinOp('person', 'person.id', 'employee', 'employee.id', '='),
                                    JoinOp('manager', 'manager.emplid', 'employee', 'employee.id', '=')])
        self.assertEqual(query.joinClause, expectedJoins)
        expectedSelectCols = [ColumnRef.create('person.id', 'person'),
                              FuncCall.create('avg', [ColumnRef.create('person.age', 'person')])]
        self.assertEqual(query.selectColumns, expectedSelectCols)
        expectedTables = {'person', 'employee', 'manager'}
        self.assertEqual(query.tables, expectedTables)
        self.assertIsNone(query.groupClause)
        self.assertIsNone(query.whereClause)

    def testTripleJoin(self):
        query = Query('''select person.id, avg(person.age) from person
            join employee on person.id = employee.id
            join manager on manager.emplid = employee.id
            join exec on exec.id = manager.execid''')
        expectedJoins = JoinClause([JoinOp('person', 'person.id', 'employee', 'employee.id', '='),
                                    JoinOp('manager', 'manager.emplid', 'employee', 'employee.id', '='),
                                    JoinOp('exec', 'exec.id', 'manager', 'manager.execid', '=')])
        self.assertEqual(query.joinClause, expectedJoins)
        firstSelectCol = ColumnRef.create('person.id', 'person')
        secondSelectCol = FuncCall.create('avg', [ColumnRef.create('person.age', 'person')])
        expectedSelectCols = [firstSelectCol, secondSelectCol]
        self.assertEqual(query.selectColumns, expectedSelectCols)
        expectedTables = {'person', 'employee', 'manager', 'exec'}
        self.assertEqual(query.tables, expectedTables)
        self.assertIsNone(query.groupClause)
        self.assertIsNone(query.whereClause)

    def testFunc(self):
        query = Query('''select count(*) from person''')
        expectedSelectCols = [FuncCall.create('count', [ColumnRef.create('*', None)])]
        self.assertEqual(query.selectColumns, expectedSelectCols)
        self.assertIsNone(query.joinClause)
        expectedTables = {'person'}
        self.assertEqual(query.tables, expectedTables)
        self.assertIsNone(query.groupClause)
        self.assertIsNone(query.whereClause)

    def testSimpleWhereClause(self):
        query = Query('''select * from utterance, billdiscussion, bill, hearing, person
                        where utterance.did = billdiscussion.did
                        and billdiscussion.bid = bill.bid
                        and billdiscussion.hid = hearing.hid
                        and utterance.pid = person.pid;''')
        self.assertEqual(query.tables, {'utterance', 'billdiscussion', 'bill', 'hearing', 'person'})
        expectedWhere = WhereClause([BinaryOp(ColumnRef.create('utterance.did', 'utterance'),
                                              ColumnRef.create('billdiscussion.did', 'billdiscussion'),
                                              '='),
                                     BinaryOp(ColumnRef.create('billdiscussion.bid', 'billdiscussion'),
                                              ColumnRef.create('bill.bid', 'bill'),
                                              '='),
                                     BinaryOp(ColumnRef.create('billdiscussion.hid', 'billdiscussion'),
                                              ColumnRef.create('hearing.hid', 'hearing'),
                                              '='),
                                     BinaryOp(ColumnRef.create('utterance.pid', 'utterance'),
                                              ColumnRef.create('person.pid', 'person'),
                                              '=')])
        self.assertEqual(query.whereClause, expectedWhere)
        self.assertEqual(query.selectColumns, [ColumnRef.create('*', None)])
        self.assertIsNone(query.joinClause)
        self.assertIsNone(query.groupClause)

    def testWhereClauseLike(self):
        query = Query('''select * from bill where bill.status like "%et%";''')
        expectedWhere = WhereClause([BinaryOp(ColumnRef.create('bill.status', 'bill'),
                                              ColumnRef.create('%et%', None),
                                              '~~')])
        self.assertEqual(query.whereClause, expectedWhere)
        expectedSelect = [ColumnRef.create('*', None)]
        self.assertEqual(query.selectColumns, expectedSelect)
        self.assertIsNone(query.joinClause)
        self.assertEqual(query.tables, {'bill'})
        self.assertIsNone(query.groupClause)
        self.assertEqual(str(query), 'select * from bill where bill.status like \'%et%\';')

    def testSimpleGroupBy(self):
        query = Query('''select person.first, person.last, count(*)
                        from person join term on person.pid = term.pid
                        group by person.pid, person.last;''')
        self.assertEqual(query.tables, {'person', 'term'})
        self.assertEqual(query.joinClause, JoinClause(
            [JoinOp('person', 'person.pid', 'term', 'term.pid', '=')]))
        expectedSelect = [ColumnRef.create('person.first', 'person'),
                          ColumnRef.create('person.last', 'person'),
                          FuncCall.create('count', [ColumnRef.create('*', None)])]
        self.assertEqual(query.selectColumns, expectedSelect)
        self.assertIsNone(query.whereClause)
        self.assertEqual(query.groupClause,
                         GroupClause([ColumnRef.create('person.pid', 'person'),
                                      ColumnRef.create('person.last', 'person')]))
        self.assertEqual(str(query), 'select person.first, person.last, count(*)'
                         + ' from person join term on person.pid = term.pid'
                         + ' group by person.pid, person.last;')

    def testGroupByFunc(self):
        query = Query('''select person.pid, count(*) from person
                        join term on person.pid = term.pid
                        group by count(*), person.pid''')
        self.assertEqual(query.tables, {'person', 'term'})
        self.assertEqual(query.selectColumns,
                         [ColumnRef.create('person.pid', 'person'),
                          FuncCall.create('count', [ColumnRef.create('*', None)])])
        self.assertEqual(query.joinClause,
                         JoinClause([JoinOp('person', 'person.pid', 'term', 'term.pid', '=')]))
        self.assertIsNone(query.whereClause)
        self.assertEqual(query.groupClause,
                         GroupClause([FuncCall.create('count', [ColumnRef.create('*', None)]),
                                      ColumnRef.create('person.pid', 'person')]))
        self.assertEqual(str(query), 'select person.pid, count(*) from person '
                         + 'join term on person.pid = term.pid '
                         + 'group by count(*), person.pid;')


if __name__ == '__main__':
    unittest.main()
