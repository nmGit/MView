# Copyright 2018 Noah Meltzer

__author__ = "Noah Meltzer"
__copyright__ = "Copyright 2018"
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Noah Meltzer"
__status__ = "Beta"

import sqlite3
from datetime import date
import time
import traceback

class MDataBase:
    def __init__(self, db_path):
        print "Connecting to database located at:", db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    def save(self, table_name, column_names, value_names):

        values = [str(v) for v in value_names]
        values = "'"+"','".join(values)+"'"

        columns = ",".join(column_names)
        table_name = table_name.replace(" ", "_")

        #print "trying to save:\n\t", columns, "\n\t", values
        try:
            self.cursor.execute(
                "INSERT INTO {tn} ({cn})"
                "VALUES ({vals});".format(
                    tn = table_name,
                    cn = columns,
                    vals = values
                    )
                )
            print self.cursor.fetchall()
            self.conn.commit()
            return True
        except:
            traceback.print_exc()
            return False


    def create_table(self, column_names, column_qualifiers, table_name):
        table_name = table_name.replace(" ", "_")
        column_tup = []
        for i,c in enumerate(column_names):
            column_tup.append(str(c)+" "+str(column_qualifiers[i]))
        columns = ",".join(column_tup)
        print "Creating table:", table_name, "with columns:", columns
        self.cursor.execute(
             "CREATE TABLE {tn}("
             "   PK INTEGER PRIMARY KEY AUTOINCREMENT,"
             "   {cn}"
             ");".format(
                 tn = table_name,
                 cn = columns
             )
        )

    def does_table_exist(self, table_name):
        table_name = table_name.replace(" ","_")
        self.cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE TYPE='table' AND NAME='{tn}'".format(tn=table_name))
        return (1==self.cursor.fetchall()[0][0])

    def saveState(self):
        pass
    def restoreState(self):
        pass
    def configureDataSets(self):
        pass
    def closeDataSet(self):
        self.conn.commit()
        self.conn.close()
    def __addColumn(self):
        pass