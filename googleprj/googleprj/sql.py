import MySQLdb
from  googleprj import settings
from datetime import datetime


db = MySQLdb.connect(settings.MYSQL_HOST, settings.MYSQL_USER, settings.MYSQL_PASSWORD, settings.MYSQL_DB)
cursor = db.cursor()


class Sql:
    @classmethod
    def insert_brand(self,item):
        sql = "REPLACE  INTO tb_unavaliable_google (asin,url,bigname,brand,keyword,score,comment) VALUES ('%s', '%s', '%s', '%s','%s','%s','%s')" % (item['asin'],item['url'],item['bigname'],item['brand'],item['keyword'],item['score'],item['comment'])
        try:
            cursor.execute(sql)
            db.commit()
        except Exception,e:
            print 'iiiiiiiiiiiiiiin'
            print e
            db.rollback()
    
    @classmethod
    def insert_gurl(self,item):
        sql = "replace INTO tb_tempurl (url,keyword,isvalid) VALUES ('%s', '%s','%s')" % (item['url'],item['keyword'],item['isvalid'])
        try:
            cursor.execute(sql)
            db.commit()
        except Exception,e:
            print e
            db.rollback()

    @classmethod
    def insert_burl(self,item):
        sql = "replace INTO tb_tempurl2 (url,keyword,isvalid) VALUES ('%s', '%s','%s')" % (item['url'],item['keyword'],item['isvalid'])
        try:
            cursor.execute(sql)
            db.commit()
        except Exception,e:
            print e
            db.rollback()
    
    @classmethod
    def insert_ukurl(self,item):
        sql = "replace INTO tb_ukurl (url,keyword,isvalid) VALUES ('%s', '%s','%s')" % (item['url'],item['keyword'],item['isvalid'])
        try:
            cursor.execute(sql)
            db.commit()
        except Exception,e:
            print e
            db.rollback()
            
    @classmethod
    def insert_deurl(self,item):
        sql = "replace INTO tb_deurl (url,keyword,isvalid) VALUES ('%s', '%s','%s')" % (item['url'],item['keyword'],item['isvalid'])
        try:
            cursor.execute(sql)
            db.commit()
        except Exception,e:
            print e
            db.rollback()