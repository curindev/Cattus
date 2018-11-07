# file.py
#
# Copyright 2018 Francisco
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

import xlsxwriter, csv, os
from .connection import SQLUtils

class Buffer(): # class for textbuffer manipulation
    def __init__(self):
        self.BUFFER = None
        self.START = None
        self.END = None
        
    def start(self, buffer): #initialize buffer vars
        self.BUFFER = buffer
        self.START = self.BUFFER.get_start_iter()
        self.END = self.BUFFER.get_end_iter()
        
    def close(self): # Close buffer vars
        self.BUFFER = None
        self.START = None
        self.END = None    
        
    def delete(self): # delete text from buffer
        self.BUFFER.delete(self.START, self.END)
        
    def text(self): # return text int buffer
        return self.BUFFER.get_text(self.START, self.END, True)
        
    def open_file(self, url): #open file in buffer
        if url is not None:
            with open(url, 'r', encoding='utf-8') as sqlFile:
                self.delete()
                text = ""
                for line in sqlFile:
                    text += line
                self.BUFFER.insert(self.END, text, -1)
                
    def save_file(self, url): # save buffer in file
        with open(url, 'w', encoding='utf-8') as sqlFile:
                text = self.BUFFER = self.text()                
                for i in text:
                    sqlFile.write(i)    

class File():
    def __init__(self):
        self.buffer = Buffer()
        self.sqlUtils = SQLUtils()

    def open_sql_file_to_editor(self, url, editorBuffer):
        self.buffer.start(editorBuffer)
        self.buffer.open_file(url)
        self.buffer.close()
        
    def save_sql_file_from_editor(self, url,editorBuffer):
        self.buffer.start(editorBuffer)
        self.buffer.save_file(url)
        self.buffer.close()

    def save_as_sql_file_from_editor(self, url, editorBuffer):
        self.buffer.start(editorBuffer)
        self.buffer.save_file(url)
        self.buffer.close()
        
    def save_xlsx_file(self, directory, table, columns, rows):
        book = xlsxwriter.Workbook(directory+os.path.sep+table+".xlsx")
        booksheet = book.add_worksheet()
        booksheet.set_column(1, 1, len(rows))

        listModel = list(rows)
        listModel.insert(0, columns)

        for row, item in enumerate(listModel):
            booksheet.write_row(row, 0, item)
            
        book.close()

    def save_csv_file(self, directory, table, columns, rows):
        listModel = list(rows)
        listModel.insert(0, columns)

        csvFile = open(directory+os.path.sep+table+".csv", 'w')
        with csvFile:
            writer = csv.writer(csvFile)
            writer.writerows(listModel)
        csvFile.close()
        
        
    def generate_scrip(self,name, scheme, columns, rows):     
        s = str(columns)
        r = s.replace('[', "")
        t = r.replace(']', "")
        y = t.replace('\'', "")
        
        
        script = ""
        scriptScheme = ""
        
        scriptScheme += "--EXPORTED FROM CATTUS VISUALIZER 1.0\n\n"
        scriptScheme += "--{0}\n\n".format(name) 
        scriptScheme += "{0};\n\n".format(scheme[0][0])
        scriptScheme += "--Inserting data in table{0}\n\n".format(name)
                
        for r in rows:
            s = str(r)
            r = s.replace('[', "")
            t = r.replace(']', "")
            
            
            script += "INSERT INTO {0}({1}) VALUES({2});\n".format(name,y,t)
        
        text = self.sqlUtils.upper(scriptScheme+script)
        return text+"\n\n"
                   
        
        
    def save_sql_script_one_file(self,url,script):
        with open(url, 'w', encoding='utf-8') as s:
            b = script.decode('utf8')
            s.write(b)
                        
        
    def save_sql_script_file(self,path,url,script):
        with open(path+os.path.sep+url, 'w', encoding='utf-8') as s:
            s.write(script)
                
