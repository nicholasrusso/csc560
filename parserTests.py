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
        query = Query('''select person.id, avg(person.age) as avg_age from person
            join employee on person.id = employee.id
            join manager on manager.emplid = employee.id
            join exec on exec.id = manager.execid''')
        expectedJoins = JoinClause([JoinOp('person', 'person.id', 'employee', 'employee.id', '='),
                                    JoinOp('manager', 'manager.emplid', 'employee', 'employee.id', '='),
                                    JoinOp('exec', 'exec.id', 'manager', 'manager.execid', '=')])
        self.assertEqual(query.joinClause, expectedJoins)
        firstSelectCol = ColumnRef.create('person.id', 'person')
        secondSelectCol = QueryAlias('avg_age',
                                     FuncCall.create('avg',
                                                     [ColumnRef.create('person.age', 'person')]))
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

    def testIsNull(self):
        query = Query('select * from legislator where legislator.twitter_handle is null;')
        self.assertEqual(query.tables, {'legislator'})
        self.assertEqual(query.selectColumns,
                         [ColumnRef.create('*', None)])
        self.assertEqual(query.whereClause,
                         WhereClause([NullTest(ColumnRef.create('legislator.twitter_handle',
                                                                'legislator'),
                                               True)]))
        self.assertIsNone(query.joinClause)
        self.assertIsNone(query.groupClause)

    def testIsNotNull(self):
        query = Query('select * from legislator where legislator.twitter_handle is not null;')
        self.assertEqual(query.tables, {'legislator'})
        self.assertEqual(query.selectColumns,
                         [ColumnRef.create('*', None)])
        self.assertEqual(query.whereClause,
                         WhereClause([NullTest(ColumnRef.create('legislator.twitter_handle',
                                                                'legislator'),
                                               False)]))
        self.assertIsNone(query.joinClause)
        self.assertIsNone(query.groupClause)

    def testConst(self):
        query = Query('''select * from person join term on person.pid = term.pid
                        where person.first like \'A%\' and term.current_term = 1;''')
        self.assertEqual(query.tables, {'person', 'term'})
        self.assertEqual(query.selectColumns,
                         [ColumnRef.create('*', None)])
        self.assertEqual(query.joinClause,
                         JoinClause([JoinOp('person', 'person.pid', 'term', 'term.pid', '=')]))
        expectedWhere = WhereClause([BinaryOp(ColumnRef.create('person.first', 'person'),
                                              Constant('A%', STRING_TYPE),
                                              LIKE),
                                     BinaryOp(ColumnRef.create('term.current_term', 'term'),
                                              Constant(1, INTEGER_TYPE),
                                              '=')])
        self.assertEqual(query.whereClause, expectedWhere)
        self.assertIsNone(query.groupClause)

    def testQueryAliases(self):
        query = Query('''select lineitem.l_returnflag, lineitem.l_linestatus,
                        sum(lineitem.l_quantity) as sum_qty,
                        sum(lineitem.l_extendedprice) as sum_base_price,
                        avg(lineitem.l_quantity) as avg_qty,
                        avg(lineitem.l_extendedprice) as avg_price,
                        avg(lineitem.l_discount) as avg_disc,
                        count(*) as count_order from lineitem
                        where lineitem.l_shipdate <= '1998-12-01'
                        group by lineitem.l_returnflag, lineitem.l_linestatus
                        order by lineitem.l_returnflag, lineitem.l_linestatus;''')
        self.assertEqual(query.tables, {'lineitem'})
        self.assertEqual(query.selectColumns,
                         [ColumnRef.create('lineitem.l_returnflag', 'lineitem'),
                          ColumnRef.create('lineitem.l_linestatus', 'lineitem'),
                          QueryAlias('sum_qty',
                                     FuncCall.create('sum',
                                                     [ColumnRef.create('lineitem.l_quantity',
                                                                       'lineitem')])),
                          QueryAlias('sum_base_price',
                                     FuncCall.create('sum',
                                                     [ColumnRef.create('lineitem.l_extendedprice',
                                                                       'lineitem')])),
                          QueryAlias('avg_qty',
                                     FuncCall.create('avg',
                                                     [ColumnRef.create('lineitem.l_quantity',
                                                                       'lineitem')])),
                          QueryAlias('avg_price',
                                     FuncCall.create('avg',
                                                     [ColumnRef.create('lineitem.l_extendedprice',
                                                                       'lineitem')])),
                          QueryAlias('avg_disc',
                                     FuncCall.create('avg',
                                                     [ColumnRef.create('lineitem.l_discount',
                                                                       'lineitem')])),
                          QueryAlias('count_order',
                                     FuncCall.create('count',
                                                     [ColumnRef.create('*', None)]))])
        self.assertEqual(query.whereClause,
                         WhereClause(
                             [BinaryOp(ColumnRef.create('lineitem.l_shipdate', 'lineitem'),
                                       Constant('1998-12-01', STRING_TYPE),
                                       '<=')]))
        self.assertEqual(query.groupClause,
                         GroupClause(
                             [ColumnRef.create('lineitem.l_returnflag', 'lineitem'),
                              ColumnRef.create('lineitem.l_linestatus', 'lineitem')]))
        self.assertIsNone(query.joinClause)

    def testBinopsInFuncs(self):
        self.maxDiff = None
        query = Query(
            '''select lineitem.l_returnflag, lineitem.l_linestatus,
                sum(lineitem.l_quantity) as sum_qty,
                sum(lineitem.l_extendedprice) as sum_base_price,
                sum(lineitem.l_extendedprice * (1 - lineitem.l_discount)) as sum_disc_price,
                sum(lineitem.l_extendedprice *
                    (1 - lineitem.l_discount) * (1 + lineitem.l_tax)) as sum_charge,
                 avg(lineitem.l_quantity) as avg_qty, avg(lineitem.l_extendedprice) as avg_price,
                 avg(lineitem.l_discount) as avg_disc, count(*) as count_order
                 from lineitem
                 where lineitem.l_shipdate <= '1998-12-01'
                 group by lineitem.l_returnflag, lineitem.l_linestatus
                 order by lineitem.l_returnflag, lineitem.l_linestatus;''')
        self.assertEqual(query.tables, {'lineitem'})
        expectedSelectCols = [ColumnRef.create('lineitem.l_returnflag', 'lineitem'),
                              ColumnRef.create('lineitem.l_linestatus', 'lineitem'),
                              QueryAlias('sum_qty',
                                         FuncCall.create('sum',
                                                         [ColumnRef.create('lineitem.l_quantity',
                                                                           'lineitem')])),
                              QueryAlias('sum_base_price',
                                         FuncCall.create('sum',
                                                         [ColumnRef.create('lineitem.l_extendedprice',
                                                                           'lineitem')])),
                              QueryAlias('sum_disc_price',
                                         FuncCall.create('sum',
                                                         [BinaryOp(ColumnRef.create(
                                                             'lineitem.l_extendedprice',
                                                             'lineitem'),
                                                             BinaryOp(Constant(1, INTEGER_TYPE),
                                                                      ColumnRef.create(
                                                                          'lineitem.l_discount',
                                                                          'lineitem'),
                                                                      '-'),
                                                             '*')])),
                              QueryAlias('sum_charge',
                                         FuncCall.create('sum',
                                                         [BinaryOp(BinaryOp(
                                                             ColumnRef.create('lineitem.l_extendedprice',
                                                                              'lineitem'),
                                                             BinaryOp(Constant(1, INTEGER_TYPE),
                                                                      ColumnRef.create(
                                                                          'lineitem.l_discount',
                                                                          'lineitem'),
                                                                      '-'),
                                                             '*'
                                                         ), BinaryOp(Constant(1, INTEGER_TYPE),
                                                                     ColumnRef.create(
                                                                         'lineitem.l_tax',
                                                                         'lineitem'),
                                                                     '+'),
                                                             '*')])),
                              QueryAlias('avg_qty',
                                         FuncCall.create('avg',
                                                         [ColumnRef.create(
                                                             'lineitem.l_quantity',
                                                             'lineitem')])),
                              QueryAlias('avg_price',
                                         FuncCall.create('avg',
                                                         [ColumnRef.create(
                                                             'lineitem.l_extendedprice',
                                                             'lineitem')])),
                              QueryAlias('avg_disc',
                                         FuncCall.create('avg',
                                                         [ColumnRef.create(
                                                             'lineitem.l_discount',
                                                             'lineitem')])),
                              QueryAlias('count_order',
                                         FuncCall.create('count',
                                                         [ColumnRef.create('*', None)]))]
        self.assertEqual(query.selectColumns, expectedSelectCols)
        self.assertEqual(query.whereClause,
                         WhereClause(
                             [BinaryOp(ColumnRef.create('lineitem.l_shipdate', 'lineitem'),
                                       Constant('1998-12-01', STRING_TYPE),
                                       '<=')]))
        self.assertEqual(query.groupClause,
                         GroupClause(
                             [ColumnRef.create('lineitem.l_returnflag', 'lineitem'),
                              ColumnRef.create('lineitem.l_linestatus', 'lineitem')]))
        self.assertIsNone(query.joinClause)

    def testReplaceTable(self):
        query = Query('''select person.pid, count(*) from person
                        join term on person.pid = term.pid
                        group by count(*), person.pid''')
        query.replaceTable('person', 'matview')
        self.assertEqual(query.tables, {'matview', 'term'})
        self.assertEqual(query.selectColumns,
                         [ColumnRef.create('matview.pid', 'matview'),
                          FuncCall.create('count', [ColumnRef.create('*', None)])])
        self.assertEqual(query.joinClause,
                         JoinClause([JoinOp('matview', 'matview.pid', 'term', 'term.pid', '=')]))
        self.assertIsNone(query.whereClause)
        self.assertEqual(query.groupClause,
                         GroupClause([FuncCall.create('count', [ColumnRef.create('*', None)]),
                                      ColumnRef.create('matview.pid', 'matview')]))
        self.assertEqual(str(query), 'select matview.pid, count(*) from matview '
                         + 'join term on matview.pid = term.pid '
                         + 'group by count(*), matview.pid;')

        query.replaceTable('term', 'matview')
        self.assertEqual(query.tables, {'matview'})
        self.assertEqual(query.selectColumns,
                         [ColumnRef.create('matview.pid', 'matview'),
                          FuncCall.create('count', [ColumnRef.create('*', None)])])
        self.assertIsNone(query.joinClause)
        self.assertIsNone(query.whereClause)
        self.assertEqual(query.groupClause,
                         GroupClause([FuncCall.create('count', [ColumnRef.create('*', None)]),
                                      ColumnRef.create('matview.pid', 'matview')]))
        self.assertEqual(str(query), 'select matview.pid, count(*) from matview '
                         + 'group by count(*), matview.pid;')

        query = Query(
            '''select lineitem.l_returnflag, lineitem.l_linestatus,
                sum(lineitem.l_quantity) as sum_qty,
                sum(lineitem.l_extendedprice) as sum_base_price,
                sum(lineitem.l_extendedprice * (1 - lineitem.l_discount)) as sum_disc_price,
                sum(lineitem.l_extendedprice *
                    (1 - lineitem.l_discount) * (1 + lineitem.l_tax)) as sum_charge,
                 avg(lineitem.l_quantity) as avg_qty, avg(lineitem.l_extendedprice) as avg_price,
                 avg(lineitem.l_discount) as avg_disc, count(*) as count_order
                 from lineitem
                 where lineitem.l_shipdate <= '1998-12-01'
                 group by lineitem.l_returnflag, lineitem.l_linestatus
                 order by lineitem.l_returnflag, lineitem.l_linestatus;''')
        query.replaceTable('lineitem', 'li_matview')
        self.assertEqual(query.tables, {'li_matview'})
        expectedSelectCols = [ColumnRef.create('li_matview.l_returnflag', 'li_matview'),
                              ColumnRef.create('li_matview.l_linestatus', 'li_matview'),
                              QueryAlias('sum_qty',
                                         FuncCall.create('sum',
                                                         [ColumnRef.create('li_matview.l_quantity',
                                                                           'li_matview')])),
                              QueryAlias('sum_base_price',
                                         FuncCall.create('sum',
                                                         [ColumnRef.create('li_matview.l_extendedprice',
                                                                           'li_matview')])),
                              QueryAlias('sum_disc_price',
                                         FuncCall.create('sum',
                                                         [BinaryOp(ColumnRef.create(
                                                             'li_matview.l_extendedprice',
                                                             'li_matview'),
                                                             BinaryOp(Constant(1, INTEGER_TYPE),
                                                                      ColumnRef.create(
                                                                          'li_matview.l_discount',
                                                                          'li_matview'),
                                                                      '-'),
                                                             '*')])),
                              QueryAlias('sum_charge',
                                         FuncCall.create('sum',
                                                         [BinaryOp(BinaryOp(
                                                             ColumnRef.create('li_matview.l_extendedprice',
                                                                              'li_matview'),
                                                             BinaryOp(Constant(1, INTEGER_TYPE),
                                                                      ColumnRef.create(
                                                                          'li_matview.l_discount',
                                                                          'li_matview'),
                                                                      '-'),
                                                             '*'
                                                         ), BinaryOp(Constant(1, INTEGER_TYPE),
                                                                     ColumnRef.create(
                                                                         'li_matview.l_tax',
                                                                         'li_matview'),
                                                                     '+'),
                                                             '*')])),
                              QueryAlias('avg_qty',
                                         FuncCall.create('avg',
                                                         [ColumnRef.create(
                                                             'li_matview.l_quantity',
                                                             'li_matview')])),
                              QueryAlias('avg_price',
                                         FuncCall.create('avg',
                                                         [ColumnRef.create(
                                                             'li_matview.l_extendedprice',
                                                             'li_matview')])),
                              QueryAlias('avg_disc',
                                         FuncCall.create('avg',
                                                         [ColumnRef.create(
                                                             'li_matview.l_discount',
                                                             'li_matview')])),

                              QueryAlias('count_order',
                                         FuncCall.create('count',
                                                         [ColumnRef.create('*', None)]))]
        self.assertEqual(query.selectColumns, expectedSelectCols)
        self.assertEqual(query.whereClause,
                         WhereClause(
                             [BinaryOp(ColumnRef.create('li_matview.l_shipdate', 'li_matview'),
                                       Constant('1998-12-01', STRING_TYPE),
                                       '<=')]))
        self.assertEqual(query.groupClause,
                         GroupClause(
                             [ColumnRef.create('li_matview.l_returnflag', 'li_matview'),
                              ColumnRef.create('li_matview.l_linestatus', 'li_matview')]))
        self.assertIsNone(query.joinClause)

        query = Query('''select * from person join employee on person.id = employee.pid
                        join manager on employee.mid = manager.id
                        join exec on manager.exid = exec.id''')
        query.replaceTable('employee', 'some_matview')
        self.assertEqual(query.tables, {'person', 'some_matview', 'manager', 'exec'})
        self.assertEqual(query.joinClause,
                         JoinClause(
                             [JoinOp('person', 'person.id', 'some_matview', 'some_matview.pid', '='),
                              JoinOp('some_matview', 'some_matview.mid', 'manager', 'manager.id', '='),
                              JoinOp('manager', 'manager.exid', 'exec', 'exec.id', '=')]))
        self.assertEqual(str(query),
                         'select * from person join some_matview on person.id = some_matview.pid'
                         ' join manager on some_matview.mid = manager.id'
                         ' join exec on manager.exid = exec.id;')

        query.replaceTable('exec', 'some_matview')
        self.assertEqual(query.tables, {'person', 'some_matview', 'manager'})
        self.assertEqual(query.joinClause,
                         JoinClause(
                             [JoinOp('person', 'person.id', 'some_matview', 'some_matview.pid', '='),
                              JoinOp('some_matview', 'some_matview.mid', 'manager', 'manager.id', '=')]))
        self.assertEqual(str(query),
                         'select * from person join some_matview on person.id = some_matview.pid'
                         ' join manager on some_matview.mid = manager.id;')

        query.replaceTable('person', 'some_matview')
        self.assertEqual(query.joinClause,
                         JoinClause(
                             [JoinOp('some_matview', 'some_matview.mid', 'manager', 'manager.id', '=')]))
        self.assertEqual(str(query),
                         'select * from some_matview join manager on some_matview.mid = manager.id;')
        query.replaceTable('manager', 'some_matview')
        self.assertIsNone(query.joinClause)
        self.assertEqual(str(query), 'select * from some_matview;')

    def testQueryToStr(self):
        query = Query('''select person.pid, person.first, person.last, count(*)
                        from billdiscussion join bill on billdiscussion.bid = bill.bid
                        join utterance on utterance.did = billdiscussion.did
                        join person on person.pid = utterance.pid
                        where bill.status = "Died"
                        group by person.pid;''')
        self.assertEqual(str(query), 'select person.pid, person.first, person.last, count(*)'
                                     ' from billdiscussion join bill on billdiscussion.bid = bill.bid'
                                     ' join utterance on utterance.did = billdiscussion.did'
                                     ' join person on person.pid = utterance.pid'
                                     ' where bill.status = \'Died\''
                                     ' group by person.pid;')
        query = Query('''select person.id, avg(person.age) from person
            join employee on person.id = employee.id
            join manager on manager.emplid = employee.id''')
        self.assertEqual(str(query), 'select person.id, avg(person.age) from person'
                                     ' join employee on person.id = employee.id'
                                     ' join manager on manager.emplid = employee.id;')


if __name__ == '__main__':
    unittest.main()
