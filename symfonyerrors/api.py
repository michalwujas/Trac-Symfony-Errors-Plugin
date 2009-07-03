# -*- coding: utf-8 -*-
import MySQLdb
from trac.core import *
from trac.config import Option, IntOption    

class SymfonyErrorPeer(Component):
    """
    Symfony database related methods for fetching data
    """    
    host = Option('symfonyerrors','dbhost','localhost')
    port = IntOption('symfonyerrors','dbport','3306')
    dbname   = Option('symfonyerrors','dbname', None)
    user = Option('symfonyerrors','dbuser', None)
    passwd = Option('symfonyerrors','dbpasswd', None)
    
    def __init__(self):
        self.connect()
    
    # connect to external symfony database    
    def connect(self):
        self.db = MySQLdb.connect(host=self.host, port=self.port, user=self.user, passwd=self.passwd, db=self.dbname, charset="utf8", use_unicode=True)        
    
    # retrieve one row from symfony error table for given hash_key
    def retrieve_by_hash(self, bug_id):
        cursor = self.db.cursor()        
        cursor.execute("select message, uri, module_name, action_name, hash_key from sf_error_log where hash_key = '%s'" % bug_id)
        msg = cursor.fetchone()
        cursor.close()

        return msg
    
    # selects grouped rows from symfony error table 
    def select_grouped(self):
        self.connect()       
        cursor = self.db.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT id, request, exception_object, uri, MAX(created_at) as created_at, message, module_name, action_name, COUNT(message) as counter, hash_key FROM sf_error_log GROUP BY hash_key ORDER BY counter desc")
    
        return cursor.fetchall()
    
    # deletes rows for given hash_key
    def delete_by_hash(self, hash_key):
        self.db.query("delete from sf_error_log where hash_key = '%s'" % hash_key)

            
