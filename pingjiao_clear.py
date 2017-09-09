#coding=utf-8

import requests
import re
import json
import random
import numpy as np

#创建session，传递cookie
conn=requests.session()

#登录
print ('登录中...')
url='http://onestop.ucas.ac.cn/Ajax/Login/0'
data={
    'username':'xxx@xxx' #登录邮箱
    'password':'xxxxxx'  #登录密码
    'remember':'checked'
}
headers={
    'Accept':'*/*',
    'Accept-Encoding':'gzip, deflate',
    'Accept-Language':'zh-CN,zh;q=0.8',
    'Connection':'keep-alive',
    'Content-Length':'64',
    'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
    'Host':'onestop.ucas.ac.cn',
    'rigin':'http://onestop.ucas.ac.cn',
    'Referer':'http://onestop.ucas.ac.cn/home/index',
    'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'X-Requested-With':'XMLHttpRequest'
}
resp=conn.post(url=url,headers=headers,data=data)
print ('登陆完成！')

#进入选课系统
print ('进入评教系统...')
url=json.loads(resp.text)['msg']
resp=conn.get(url=url)

url='http://sep.ucas.ac.cn/portal/site/226/821'
resp=conn.get(url=url)

reg=r'window.location.href=\'(.+?)\''
url_reg=re.compile(reg)
url_list=url_reg.findall(resp.text)
url=url_list[0]
resp=conn.get(url=url) #访问重定向的网址 进入选课系统

#进入选择课程界面 获得query_string_paras
url='http://jwxk.ucas.ac.cn/courseManage/main'
resp=conn.get(url=url)

reg=r'\"?s=(.+?)\";'
url_reg=re.compile(reg)
query_list=url_reg.findall(resp.text)
query_string_paras=query_list[0]

#获取所选课程id号
url='http://jwxk.ucas.ac.cn/courseManage/selectedCourse'
resp=conn.get(url=url)

reg=r'courseplan/+(.+?)\"'
course_reg=re.compile(reg)
course_list=course_reg.findall(resp.text)

#评教
print ('评教中,请耐心等待...')
comment={
    '1':'老师认真负责，作业布置的也十分合理，一学期下来收获很多',
    '2':'老师讲的好，同学们听得都很认真，作业量也适中，希望老师继续保持下去',
    '3':'老师的课讲得好，作业布置的合理，好好学能有很大收获'
    }
data={str(x):'900' for x in np.arange(900)}
data_other={
    #5星 和 评价
    'starFlag':'5',
    'flaw':'',
    'suggest':''
}
data.update(data_other)
for course in course_list:
    url='http://jwxk.ucas.ac.cn/evaluate/save/'+course+'?s='+query_string_paras
    data_merit={'merit':comment[random.choice(['1','2','3'])]}
    data_new=data.copy()
    data_new.update(data_merit)
    resp=conn.post(url=url,data=data_new)
print ('评教完成！')


