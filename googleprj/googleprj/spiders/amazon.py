# -*- coding: utf-8 -*-
import scrapy
from googleprj.items import DmozItem,gurl
from lxml import etree
import re,time
import urllib
import requests
from googleprj.settings import *
from googleprj.redisM import RedisM
import MySQLdb

count = 0
rm = RedisM()
db = MySQLdb.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB)
cursor = db.cursor()

class amazon(scrapy.Spider):
    
    name = "amazon"
    allowed_domains = ["amazon.com"]
    
    def start_requests(self):
        global rm,cursor,db
        if rm.getvalue("amazonpool") == None or len(rm.getvalue("amazonpool"))<5:
            rm.pushredis("amazonpool",IPPOOL)
            
        sql = "select url from tb_tempurl where isvalid=1"
        try:
            cursor.execute(sql)
            results = cursor.fetchall()
            key = time.strftime("%d%m%Y")
            if rm.getvalue(key) == None or len(rm.getvalue(key))==0:
                rm.pushredis(key,results)
        except Exception,e:
            print e
            
        key = time.strftime("%d%m%Y")   
        #for row in rm.getvalue("amazonpool"):
        dict = eval(rm.popredis(key,"amazon_dealpool"))
        yield scrapy.Request(url=dict[0], callback=self.parse,headers=AMAZON_HEADERS,meta={'cookiejar':1})
    
    def parse(self, response):
        global count,rm,cursor,db
        count += 1
        #填充IP池
        if rm.getvalue("amazonpool") == None or len(rm.getvalue("amazonpool"))<5:
            rm.pushredis("amazonpool",IPPOOL)
            
        if(len(response.xpath('//div[@id="outOfStock"]')))>0:
            brand = ""
            if(len(response.xpath('//div[@id="bylineInfo_feature_div"]/div/a/text()')))>0:
                brand = response.xpath('//div[@id="bylineInfo_feature_div"]/div/a/text()')[0].extract()  
            elif(len(response.xpath('//div[@id="brandBylineWrapper"]/div/a')))>0:
                brand = response.xpath('//div[@id="brandBylineWrapper"]/div/a/text()')[0].extract()  

            str = response.request.url
            asin = ""
            if "dp/" in str:
                asin = str[str.find("dp/")+3:str.find("dp/")+13]
            elif "product/" in str:
                asin = str[str.find("product/")+8:str.find("product/")+18]
            elif "ASIN/" in str:
                asin = str[str.find("ASIN/")+5:str.find("ASIN/")+15]
            print asin
                
            comment = '0'
            if(len(response.xpath('//*[@id="acrCustomerReviewText"]/text()')))>0:
                comment = response.xpath('//*[@id="acrCustomerReviewText"]/text()')[0].extract() 
                    
                if "Be the first to review this item" in comment:
                    comment = "0"
                else:
                    comment = comment.replace(" customer reviews", "").replace(" customer review", "")
                    
            score = "0"
            if(len(response.xpath('//*[@id="acrPopover"]/span[1]/a/i[1]/span/text()')))>0:
                score = response.xpath('//*[@id="acrPopover"]/span[1]/a/i[1]/span/text()')[0].extract() 
                    
                if "out of 5 stars" in score:
                    score = score.replace(" out of 5 stars", "")
            
            #bigname find
            bigname = ""
            big1 = etree.HTML(response.body).xpath('//a')

            if big1!=None and len(big1)>0:
                for row in big1:
                    if len(row.xpath("@href"))>0 and 'bestsellers' in row.xpath("@href")[0] :
                        if len(row.xpath("text()"))>0:
                            txt = row.xpath("text()")[0].replace("See Top 100 in ","").replace(" ","").replace("\n","").replace("Seetop100","")
                            if txt != "See Top 100" and txt != "" and len(txt)>=4:
                                bigname = txt
                                print bigname
                                break

            item = DmozItem()
            item['asin'] = asin
            item['brand'] = brand
            item['url'] =  response.request.url
            item['keyword'] = ""
            item['score'] = score
            item['comment'] = comment
            item['bigname'] = bigname
            yield item
                
        #更新已处理url
        try:
            updatesql = "update tb_tempurl set isvalid=0 where url= '"+response.request.url+"'"
            cursor.execute(updatesql)
            db.commit()
        except Exception,e:
            print 'uuuuuuuuuuuuuu'
            print e
            db.rollback()
        
        change_proxy = False
        title = None
        if len(response.xpath('//title/text()'))>0:
            title = response.xpath('//title/text()')[0].extract()
        body = response.body
        dogimg = response.xpath('//*[@id="d"]')
        if title != None and ("Robot Check" in title or "503" in title or "service un" in title.lower()):
            change_proxy = True
        elif (dogimg != None and len(dogimg)>0) or '._TTD_.jpg' in body :
            change_proxy = True
        
        key = time.strftime("%d%m%Y")
        if len(rm.getvalue(key))>0:
            dict = eval(rm.popredis(key,"amazon_dealpool"))
            print dict[0]
            yield scrapy.Request(url=dict[0], callback=self.parse, meta={'cookiejar':response.meta['cookiejar'],'change_proxy':change_proxy,'proxy':response.request.meta["proxy"]},headers=AMAZON_HEADERS)
