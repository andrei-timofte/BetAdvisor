from db_helper import DBInterface

meciuri = DBInterface('games.db', 'test_table', {"col1": "integer PRIMARY KEY NOT NULL", 'col2': "VARCHAR(30) NOT NULL", 'col3': 'VARCHAR(30) NOT NULL'}, 'col1')
results = DBInterface('resultts.db', 'test_results', {"col1": "integer PRIMARY KEY NOT NULL", 'col2': "VARCHAR(30) NOT NULL", 'col3': 'VARCHAR(30) NOT NULL', 'col4': 'VARCHAR(30) NOT NULL'}, 'col1')
alg = DBInterface('algorithm1.db', 'alg1_results', {"col1": "integer PRIMARY KEY NOT NULL", 'col2': "VARCHAR(30) NOT NULL", 'col3': 'VARCHAR(30) NOT NULL'}, 'col1')

meciuri.insert_record({'col1': 1, 'col2': 'test1', 'col3': 'test2'})
meciuri.insert_record({'col1': 2, 'col2': 'test3', 'col3': 'test4'})
results.insert_record({'col1': 3, 'col2': 'test5', 'col3': 'test6', 'col4': 'test7'})
results.insert_record({'col1': 4, 'col2': 'test8', 'col3': 'test9', 'col4': 'test10'})
alg.insert_record({'col1': 5, 'col2': 'test8', 'col3': 'test9'})
alg.insert_record({'col1': 6, 'col2': 'test9', 'col3': 'test10'})
