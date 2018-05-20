# Copyright 2018 Noah Meltzer

__author__ = "Noah Meltzer"
__copyright__ = "Copyright 2018"
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Noah Meltzer"
__status__ = "Beta"

from datetime import datetime
import time
from MDataBase import MDataBase
from PyQt4 import QtGui, QtCore
import traceback
class MDataBaseWrapper(QtCore.QThread):

    db_params_updated_signal = QtCore.pyqtSignal(str, name="db_params_updated_signal")

    def __init__(self, device):
        super(MDataBaseWrapper, self).__init__()
        self.device = device
        self.db = None

        self.db_params_updated_signal.connect(self.openDb)

        log_location = self.device.getFrame().DataLoggingInfo()['location']
        # Make sure logging is enabled
        if log_location == None:
            self.device.log(False)
            print str(self.device), ": Datalogging not configured. This device's data logging will be turned off."
            return

        self.openDb(time.strftime("%Y_%B_%d"))

    def save(self):

        try:
            # TODO:Optimize, doesn't need to be done everytime
            columns = self.device.getParameters().keys()
            columns_with_units = []
            for col in columns:
                columns_with_units.append(col)
                columns_with_units.append("unit_"+str(col))

            columns = columns_with_units

            columns = [c.replace(' ', '_') for c in columns]

            columns.insert(0, "capture_time")
            #rows = [self.device.getReading(p) if self.device.isDataLoggingEnabled(p) else None for p in self.device.getParameters()]
            rows = []
            for param in self.device.getParameters():
                rows.append(self.device.getReading(param))
                rows.append(self.device.getUnit(param))

            rows.insert(0,datetime.now().strftime("%m/%d/%Y %H:%M:%S.%f"))
            #print "Rows:", rows
            if not self.db.save(str(self.device), columns, rows):
                if not self.db.does_table_exist(str(self.device)):
                    # The first column is the time accurate to milliseconds. Making
                    # these entries unique enures that there can be no two measurements
                    # taken at the same time. More importantly, it speeds up indexing.
                    print "Database table not found. Creating one..."
                    column_types = ['TEXT UNIQUE']
                    column_types.extend(['REAL','TEXT']*len(columns))
                    print "column types",column_types
                    self.db.create_table(columns, column_types, str(self.device))
                pass
        except:
            traceback.print_exc()
            if(self.db == None):
                self.openDb(self.device.getFrame().DataLoggingInfo()['name'])

    def openDb(self, db_name):
        log_location = self.device.getFrame().DataLoggingInfo()['location']


        db_path = log_location + "\\" + db_name
        self.db = MDataBase(db_path)

    def save_state(self):
        dataname = self.device.getFrame().DataLoggingInfo()['name']
        channels = self.device.getFrame().DataLoggingInfo()['channels']

        location = self.device.getFrame().DataLoggingInfo()['location']

        web.persistentData.persistentDataAccess(dataname, 'DataLoggingInfo', str(self.device), 'name')
        web.persistentData.persistentDataAccess(channels, 'DataLoggingInfo', str(self.device), 'channels')
        web.persistentData.persistentDataAccess(location, 'DataLoggingInfo', str(self.device), 'location')

    def restore_state(self):
        dataname = web.persistentData.persistentDataAccess(None, 'DataLoggingInfo', str(self.device), 'name')
        channels = web.persistentData.persistentDataAccess(None, 'DataLoggingInfo', str(self.device), 'channels')
        location = web.persistentData.persistentDataAccess(None, 'DataLoggingInfo', str(self.device),  'location')
        #Do a sanity check
        #print "device:", self.device
        #print "restoring location of", self.device, location
        for nickname in self.device.getFrame().getNicknames():
            if channels == None or nickname not in channels.keys():
                channels = self.device.getFrame().DataLoggingInfo()['channels']
                print "Error when retreiving logged channels in config file, restoring to", channels
        if dataname is None:
            dataname = self.device.getFrame().getTitle()

        self.device.getFrame().DataLoggingInfo()['name'] = dataname
        if channels != None:
            self.device.getFrame().DataLoggingInfo()['channels'] = channels
        self.device.getFrame().DataLoggingInfo()['location'] = location
        pass
    def query(self, field, *args):
        return self.db.query(field, *args)
        
    def configure_data_sets(self):
        pass

    def close(self):
        self.conn.commit()
        self.conn.close()
