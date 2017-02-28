"""命令行火车票查看器

Usage:
    tickets [-xh] <from> <to> <date>

Options:
	-h, --help 查看帮助
	-x		学生票

Examples:
    tickets 上海 北京 2016-10-10
    tickets -x 成都 南京 2016-10-10
"""
from docopt import docopt 
import ssl
import re
from urllib import request
import json 
import mysql.connector
import smtplib
from datetime import datetime

#定义一个类
class Trains(object): 
	
	
	def __init__(self,froms,tos,dates,options):
		self.froms=froms
		self.tos=tos
		self.dates=dates
		self.options=options
	
	#将车站转换为字符
	def station(self):
		try:
			#https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.8994
			#车站与代表车站的三字母代码对应字符串
			url = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.8971'
			a=request.urlopen(url)
			data_satations=a.read().decode('utf-8')
			#用正则表达式匹配
			stations_0 = dict(re.findall(u'([\u4e00-\u9fa5]+)\|([A-Z]+)', data_satations))
			stations=dict(stations_0)
			self.from_1=stations[self.froms]
			self.to_1=stations[self.tos]
			print(self.from_1,self.to_1)
		except BaseException  as e:
			print("车站输入有误！")
	
	#获取车票信息(json格式)	
	def url(self):
		try:
			#https://kyfw.12306.cn/otn/leftTicket/query?leftTicketDTO.train_date=2017-02-27&leftTicketDTO.from_station=HBB&leftTicketDTO.to_station=BJP&purpose_codes=ADULT
			urls="https://kyfw.12306.cn/otn/leftTicket/query?leftTicketDTO.train_date=" +self.dates+ "&leftTicketDTO.from_station="+self.from_1+"&leftTicketDTO.to_station="+self.to_1+"&purpose_codes=" +self.options
			print(urls)
			b=request.urlopen(urls)
			data=b.read().decode('utf-8')
			data1=json.loads(data)
			self.data=data1['data']
			return (self.data)
		except BaseException  as e:
			print('错误！请检查输入！')

#定义一个类处理余票数(字符转整型)
class Ticket(object):

	def __init__(self,k):
		self.k=k
		
	def change(self):
		if self.k=='有':
			self.val=999
		elif  self.k=='无':
			self.val=0
		elif re.match(r'[0-9]+',self.k):
			self.val=int(self.k)
		else :
			self.val=-1
		return(self.val)



#存储数据进入数据库		
def mysql_surver(x):
	try:
		conn = mysql.connector.connect(user='数据库用户名', password='数据库密码', database='数据库名')
		cursor = conn.cursor()
	except BaseException  as e:
		print('Mysql error!')
	#迭代处理余票数据	
	for list0 in x:
		list1=list0['queryLeftNewDTO']
		from_a=list1['from_station_name']
		to_a=list1['to_station_name']
		data_=list1['start_train_date']	
		coda=list1['station_train_code']
		print(coda)
		sw=Ticket(list1['swz_num'])
		td=Ticket(list1['tz_num'])
		yd=Ticket(list1['zy_num'])
		ed=Ticket(list1['ze_num'])
		gjrw=Ticket(list1['gr_num'])
		rw=Ticket(list1['rw_num'])
		yw=Ticket(list1['yw_num'])
		rz=Ticket(list1['rz_num'])
		yz=Ticket(list1['yz_num'])
		wz=Ticket(list1['wz_num'])
		kk=(from_a,to_a,data_,coda,sw.change(),td.change(),yd.change(),ed.change(),gjrw.change(),rw.change(),yw.change(),rz.change(),yz.change(),wz.change())
		print(kk)
		cursor.execute('insert into train_ticket (query_time,from_station,to_station,data_,coda,sw,td,yd,ed,gjrw,rw,yw,rz,yz,wz) values (now(),%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', (from_a,to_a,data_,coda,sw.change(),td.change(),yd.change(),ed.change(),gjrw.change(),rw.change(),yw.change(),rz.change(),yz.change(),wz.change()))
	print(cursor.rowcount)
	conn.commit()
	cursor.close()
	conn.close()
		
if __name__ == '__main__':
	ssl._create_default_https_context = ssl._create_unverified_context	#ssl 
	arg = docopt (__doc__)	#返回一个dict
	print(arg)
	from_0=arg['<from>']
	to_0=arg['<to>']
	date_0 = arg['<date>']
	if arg['-x'] == True:
		cl='0x00'
	else:
		cl='ADULT'
	print(from_0,to_0,date_0,cl)
	t=Trains(from_0,to_0,date_0,cl)
	t.station()
	sj=t.url()
	mysql_surver(sj)