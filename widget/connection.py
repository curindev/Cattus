# connection.py
#
# Copyright 2018 Jose Francisco
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sqlite3, sqlparse

# Initialize global sql querys for extract information
SQL_SELECT = "SELECT * FROM {0};"
SQL_COUNT = "SELECT COUNT(*) FROM sqlite_master WHERE type='{0}' AND name NOT LIKE 'sqlite_%';" # table, index, view
SQL_REMOVE = "DROP {0} {1};"
SQL_NAME_FROM_MASTER = "SELECT name FROM sqlite_master WHERE type='{0}' AND name NOT LIKE 'sqlite_%' ORDER BY name;" 
SQL_NAME_SCHEME_FROM_MASTER = "SELECT name, sql FROM sqlite_master WHERE type='{0}' and name='{1}' ORDER BY Name;" # table, index, view
SQL_SQL_FROM_MASTER = "SELECT sql FROM sqlite_master WHERE type='{0}' and name='{1}';"
SQL_PRAGMA_TABLE_INFO = "PRAGMA table_info({0});"


class Connection():
    def __init__(self):
        self.URL = None
        self.CONN = None
        self.CURSOR = None
        
    def connect(self, url):
        if url is not None:
            self.URL = url
            self.CONN = sqlite3.connect(self.URL)
            self.CONN.execute("PRAGMA foreign_keys = 1")
            self.CURSOR = self.CONN.cursor()
            print("Database Connected")      
            
    def get_connection(self):
        return self.CONN      
    
    def disconnect(self):
        if self.CONN is not None:
            self.CONN.close()
            self.CURSOR = None
            self.URL = None
            print("Database Disconnected")


class SQLMeta(Connection):
    def __init__(self):
        super().__init__()
        pass        
    
    def remove_from_master(self, type_d, name):
        if type_d is not None and name is not None:
            try:
                self.CURSOR.execute(SQL_REMOVE.format(type_d, name))
                return True
            except sqlite3.OperationalError as error:
                return False
                
    def get_data_from_query(self, query, x=False):
        if query is not None:
            data = self.CURSOR.execute(query)     
            if x == True:
                self.CONN.commit()       
            return (data.fetchall(),self.CURSOR)
    
    def get_count_type(self, type_d):
        if type_d is not None:
            data = self.CURSOR.execute(SQL_COUNT.format(type_d))
            return data.fetchone() #return tuple
    
    def get_select_all(self, table):
        if table is not None:
            data = self.CURSOR.execute(SQL_SELECT.format(table))
            return data.fetchall() #return list of tuples        
        
    def get_name_from_master(self, type_d):
        if type_d is not None:
            data = self.CURSOR.execute(SQL_NAME_FROM_MASTER.format(type_d))
            return data.fetchall() #return list of tuples
            
    def get_name_scheme_from_master(self, name, type_d):
        if type_d is not None:
            data = self.CURSOR.execute(SQL_NAME_SCHEME_FROM_MASTER.format(type_d, name))
            return data.fetchall() #return list of tuples    
            
    def get_scheme_from_master(self, name, type_d):
        if type_d is not None:
            data = self.CURSOR.execute(SQL_SQL_FROM_MASTER.format(type_d, name))
            return data.fetchall()
            
    def get_table_info(self, table):
        if table is not None:
            data = self.CURSOR.execute(SQL_PRAGMA_TABLE_INFO.format(table))
            return data.fetchall() #return list of tuples        

class SQLUtils():
    def __init__(self):
        pass
        
    def convert_tuple_to_list(self, data):
        if data is not None:
            tmp = []
            for item in data:
                d = list(item)
                d = list(map(str, d))
                tmp.append(d)
            return tmp

                    
    def is_nn(self, data): #is not null
        if(str(data) == "1"):
            return "✔️"
        else:
            return ""
            
    def is_pk(self, data): #is pk
        if(str(data) == "1"):
            return "🔑"
        else:
            return ""
    
    def lower(self, sql):
        return sqlparse.format(sql,reindent=False,keyword_case='lower') #return sql lower case
        
    def format_lower(self, sql):
        return sqlparse.format(sql,reindent=True,keyword_case='lower') #return sql lower case and formated
        
    def upper(self, sql):
        return sqlparse.format(sql,reindent=False,keyword_case='upper') #return sql upper case

    def format_upper(self, sql):
        return sqlparse.format(sql,reindent=True,keyword_case='upper') #return sql upper case and formated
        
    def capitalize(self, sql):
        return sqlparse.format(sql,reindent=False,keyword_case='capitalize') #return sql capitalize case

    def format_capitalize(self, sql):
        return sqlparse.format(sql,reindent=True,keyword_case='capitalize') #return sql capitalize case and formated        


# Test
#con = SQLMeta()
#con.connect("/home/francisco/Desktop/neptuno.db")
#print(con.get_count_type('table'))
#print(con.get_count_type('index'))
#print(con.get_count_type('view'))
#print(con.get_name_from_master('table'))
#print(con.get_name_from_master('index'))
#print(con.get_name_from_master('view'))
#print(con.get_name_scheme_from_master('table'))
#con.disconnect()

#con.connect("/home/francisco/Desktop/guatemala.db")
#print(con.get_count_type('table'))
#print(con.get_count_type('index'))
#print(con.get_count_type('view'))
#print(con.get_name_from_master('table'))
#print(con.get_name_from_master('index'))
#print(con.get_name_from_master('view'))
#print(con.get_table_info('Departamentos'))
#print(con.get_select_all('Departamentos'))
#con.disconnect()
#    
#u = SQLUtils()
#print(u.is_nn(1))
#print(u.is_pk(1))
#print(u.lower("select * from Usuarios;"))
#print(u.upper("select * from Usuarios;"))

