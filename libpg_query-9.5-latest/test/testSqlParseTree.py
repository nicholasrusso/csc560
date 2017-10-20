from mypgparse import queryToJsonTree

if __name__ == '__main__':
    q1 = queryToJsonTree('select id, avg(age) from person join employee on person.id = employee.id;')
    print(q1)
    
    q2 = queryToJsonTree('select * from something;')
    print(q2)
    
    q3 = queryToJsonTree('''select count(*), department.name from employee join 
        department on employee.deptId = id group by department.name''')
    print(q3)