"""命令行火车票查看器

Usage:
    tickets [-xh] <from> <to> <date> <seat> <email>

Options:
	-h, --help 查看帮助
	-x		学生票

Examples:
    tickets 上海 北京 2016-10-10 硬座 123@abc.com
    tickets -x 成都 南京 2016-10-10 133@bbc.com
"""
from docopt import docopt 
import ssl
import re
from urllib import request
import json 
import smtplib
from datetime import datetime
from email.mime.text import MIMEText

#定义一个类
class Trains(object): 
	
	
	def __init__(self,froms,tos,dates,seats,emails,options):
		self.froms=froms
		self.tos=tos
		self.dates=dates
		self.seat=seats
		self.email=emails
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
#			return (self.data)
		except BaseException  as e:
			print('错误！请检查输入！')
			
#统计各坐席余票信息			
	def remaining(self):
		self.sw=0
		self.td=0
		self.yd=0
		self.ed=0
		self.gjrw=0
		self.rw=0
		self.yw=0
		self.rz=0
		self.yz=0
		self.wz=0
		for list0 in self.data:
			list1=list0['queryLeftNewDTO']
			from_a=list1['from_station_name']
			to_a=list1['to_station_name']
			data_=list1['start_train_date']	
			coda=list1['station_train_code']
			self.coda=coda
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
			self.sw=sw.change()+self.sw
			self.td=td.change()+self.td
			self.yd=yd.change()+self.yd
			self.ed=ed.change()+self.ed
			self.gjrw=gjrw.change()+self.gjrw
			self.rw=rw.change()+self.rw
			self.yw=yw.change()+self.yw
			self.rz=rz.change()+self.rz
			self.yz=yz.change()+self.yz
			self.wz=wz.change()+self.wz
		kk=(from_a,to_a,data_,self.sw,self.td,self.yd,self.ed,self.gjrw,self.rw,self.yw,self.rz,self.yz,self.wz)
		print(kk)

#处理票种类信息		
#商务座	特等座	一等座	二等座	高级软卧	软卧	硬卧	软座	硬座	无座	其他
	def emailchoice (self):
		print(self.seat)
		if self.seat=='商务座': 
			self.z=self.sw
		elif self.seat=='特等座':
			self.z=self.td
		elif self.seat=='一等座':
			self.z=self.yd
		elif self.seat=='二等座':
			self.z=self.ed
		elif self.seat=='高级软卧':
			self.z=self.gjrw
		elif self.seat=="软卧":
			self.z=self.rw
		elif self.seat=='硬卧':
			self.z=self.yw
		elif self.seat=='软座':
			self.z=self.rz
		elif self.seat=='硬座':
			self.z=self.yz
		elif self.seat=='无座':
			self.z=self.wz
		else :
			print('print error')
			self.z=0
		return (self.z)
	
#邮件发送
	def mailoutput(self):
		mail_host = 'XXXXXXXXXXXXXXXX'  #邮件服务器 
		mail_user = 'XXXXXXXXXXXXXXXX'  #邮箱用户名
		mail_pass = 'XXXXXXXXXXXXXXXX'  #邮箱密码
		sender = 'xuwei@xu-wei.cn'  
		receivers = self.email  
		#设置email信息
		#邮件内容设置
		now = datetime.now() 
		cont= '现在是：'+str(now)+'，'+self.dates+self.froms+'到'+self.tos+'现有'+str(self.seat)+'票：'+str(self.z)+'张。'
		print(cont)
		message = MIMEText(cont,'plain','utf-8')
		#邮件主题       
		message['Subject'] = 'title' 
		#发送方信息
		message['From'] = sender 
		#接受方信息     
		message['To'] = receivers  
		#登录并发送邮件
		try:
			smtpObj = smtplib.SMTP_SSL(mail_host)
			#登录到服务器
			smtpObj.login(mail_user,mail_pass) 
			#发送
			smtpObj.sendmail(sender,receivers,message.as_string()) 
			#退出
			smtpObj.quit() 
			print('success')
		except smtplib.SMTPException as e:
			print('error',e) #打印错误
	
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
			self.val=0
		return(self.val)



		
if __name__ == '__main__':
	ssl._create_default_https_context = ssl._create_unverified_context	#ssl 
	arg = docopt (__doc__)	#返回一个dict
	print(arg)
	from_0=arg['<from>']
	to_0=arg['<to>']
	date_0 = arg['<date>']
	seat_0= arg['<seat>']
	email_0 = arg['<email>']
	if arg['-x'] == True:
		cl='0x00'
	else:
		cl='ADULT'
	print(from_0,to_0,date_0,seat_0,email_0,cl)
	t=Trains(from_0,to_0,date_0,seat_0,email_0,cl)
	t.station()
	t.url()
	t.remaining()
	yp=t.emailchoice()
	if yp >0 :
		t.mailoutput()
		
