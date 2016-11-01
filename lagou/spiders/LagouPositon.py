# -*- coding: utf-8 -*-
import scrapy
import json
from lagou.items import LagouItem
#from scrapy_redis.spiders import RedisSpider

class LagoupositonSpider(scrapy.Spider):
    name = "LagouPositon"
    #allowed_domains = ["lagou.com/zhaopin/"]
    start_urls = [
        'http://www.lagou.com/zhaopin/'
    ]
    totalPageCount = 0
    curpage = 1
    cur = 0
    myurl = 'http://www.lagou.com/jobs/positionAjax.json?'

    city = u'北京'
    kds = [u'项目经理', 'java','python','C++','unity']
    #kds = [u'项目经理']
    #kds = ['HTML5','Android','iOS',u'web前端','Flash','U3D','COCOS2D-X']
    #kds = [u'spark','MySQL','SQLServer','Oracle','DB2','MongoDB' 'ETL','Hive',u'数据仓库','Hadoop']
    #kds = [u'大数据',u'云计算',u'docker',u'中间件']
    kd = kds[0]

    headers = {
        "Host":"onlinelibrary.wiley.com",
      "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
      "Accept-Language":"zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
      "Accept-Encoding":"gzip, deflate",
      "Referer":"http://onlinelibrary.wiley.com/journal/10.1002/(ISSN)1521-3773",
      "Cookie":"EuCookie='this site uses cookies'; __utma=235730399.1295424692.1421928359.1447763419.1447815829.20; s_fid=2945BB418F8B3FEE-1902CCBEDBBA7EA2; __atuvc=0%7C37%2C0%7C38%2C0%7C39%2C0%7C40%2C3%7C41; __gads=ID=44b4ae1ff8e30f86:T=1423626648:S=ALNI_MalhqbGv303qnu14HBk1HfhJIDrfQ; __utmz=235730399.1447763419.19.2.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; TrackJS=c428ef97-432b-443e-bdfe-0880dcf38417; OLProdServerID=1026; JSESSIONID=441E57608CA4A81DFA82F4C7432B400F.f03t02; WOLSIGNATURE=7f89d4e4-d588-49a2-9f19-26490ac3cdd3; REPORTINGWOLSIGNATURE=7306160150857908530; __utmc=235730399; s_vnum=1450355421193%26vn%3D2; s_cc=true; __utmb=235730399.3.10.1447815829; __utmt=1; s_invisit=true; s_visit=1; s_prevChannel=JOURNALS; s_prevProp1=TITLE_HOME; s_prevProp2=TITLE_HOME",
      "Connection":"keep-alive"
    }

    def start_requests(self):
        # for self.kd in self.kds:
        #
        #     scrapy.http.FormRequest(self.myurl,
        #                                 formdata={'pn':str(self.curpage),'kd':self.kd},callback=self.parse)

         #查询特定关键词的内容，通过request
         return [scrapy.http.FormRequest(self.myurl,
                                        formdata={'pn':str(self.curpage),'kd':self.kd}, headers = self.headers, callback=self.parse)]

    def parse(self, response):
        print response.body
        fp = open('1.html','w')
        fp.write(response.body)
        item = LagouItem()
        jdict = json.loads(response.body)
        jcontent = jdict["content"]
        jposresult = jcontent["positionResult"]
        jresult = jposresult["result"]
        #计算总页数，取消30页的限制
        self.totalPageCount = jposresult['totalCount'] /15 + 1;
        # if self.totalPageCount > 30:
        #     self.totalPageCount = 30;
        for each in jresult:
            item['city']=each['city']
            #item['companyName'] = each['companyName']
            item['companySize'] = each['companySize']
            item['positionName'] = each['positionName']
            #item['positionType'] = each['positionType']
            sal = each['salary']
            sal = sal.split('-')
            #print sal
            #把工资字符串（ak-bk）转成最大和最小值(a,b)
            if len(sal) == 1:
                item['salaryMax'] = int(sal[0][:sal[0].find('k')])
            else:
                item['salaryMax'] = int(sal[1][:sal[1].find('k')])
            item['salaryMin'] = int(sal[0][:sal[0].find('k')])

            if item['salaryMin'] < 10000:
                continue

            item['salaryAvg'] = (item['salaryMin'] + item['salaryMax'])/2
            item['positionAdvantage'] = each['positionAdvantage']
            item['companyLabelList'] = each['companyLabelList']
            item['keyword'] = self.kd
            yield item
        if self.curpage <= self.totalPageCount:
            self.curpage += 1
            yield scrapy.http.FormRequest(self.myurl,
                                        formdata = {'pn': str(self.curpage), 'kd': self.kd},headers = self.headers, callback=self.parse)
        elif self.cur < len(self.kds)-1:
            self.curpage = 1
            self.totalPageCount = 0
            self.cur += 1
            self.kd = self.kds[self.cur]
            yield scrapy.http.FormRequest(self.myurl,
                                        formdata = {'pn': str(self.curpage), 'kd': self.kd},headers = self.headers, callback=self.parse)

