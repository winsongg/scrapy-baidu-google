# -*- coding: utf-8 -*-
from settings import *
import MySQLdb

db = MySQLdb.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB)
cursor = db.cursor()

def test():
        
    sql = "select keyword from tb_keywords where isvalid=1"
    cursor.execute(sql)
    keywords = cursor.fetchall()
    print keywords

if __name__=="__main__":
      test()      