#coding=utf-8

import requests
import re
import json
import time

conn=requests.session() #创建session，传递cookie
del_flag=0 #删除课程flag
add_flag=1 #新增课程flag

#登录
print ('登录中...')

'''
#第一种登录方式
url='http://onestop.ucas.ac.cn/Ajax/Login/0'
data={
    'username':'xxx@xxx', #登录邮箱
    'password':'xxxxxx',  #登录密码
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
print ('进入选课系统...')
url=json.loads(resp.text)['msg']
resp=conn.get(url=url)
'''

#第二种登录方式
url='http://sep.ucas.ac.cn/slogin'
headers={
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding':'gzip, deflate',
    'Accept-Language':'zh-CN,zh;q=0.8',
    'Cache-Control':'max-age=0',
    'Connection':'keep-alive',
    'Content-Length':'61',
    'Content-Type':'application/x-www-form-urlencoded',
    'Host':'sep.ucas.ac.cn',
    'Origin':'http://sep.ucas.ac.cn',
    'Referer':'http://sep.ucas.ac.cn/',
    'Upgrade-Insecure-Requests':'1',
    'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'
}
data={
    'userName':'xxx@xxx', #登录邮箱
    'pwd':'xxxxxx',       #登录密码
    'sb':'sb'
}
resp=conn.post(url=url,headers=headers,data=data)

#准备进入选课系统
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

#退课
if del_flag:
    course_list=[   #构造要删除的课程号列表
        136034
        136064
    ]
    count=1
    while 1:
        print('=====================Round '+str(count)+'=========================')
        count=count+1
        if not course_list:
            print ('课程全部退课成功！')
            break
        for i in course_list:
            url_del='http://jwxk.ucas.ac.cn/courseManage/del/'+str(i)+'?s='+query_string_paras
            try:
                resp=conn.get(url=url_del,timeout=3)
            except:
                continue
            success_reg=re.compile(u'成功')
            if success_reg.search(resp.text):
                course_list.remove(i)    #从列表中删除这一门课
                print (str(i)+' 退课成功！')
            else:
                print (str(i)+' 退课失败！')

        time.sleep(1)

#选课
if add_flag:
    '''
    需要手动构造data：
    1.deptIds为学院id，即你要选的课程属于哪个学院
    01-数学：910
    02-物理：911
    03-天文：957
    04-化学：912
    05-材料：928
    06-生命：913
    07-地球：914
    08-资环：921
    09-计算机：951
    10-电子：952
    11-工程：958
    12-经管：917
    13-公共管理：945
    14-人文：927
    15-外语：915
    16-中丹：954
    17-国际：955
    18-存济：959
    19-微电子：961
    20-网络空间安全：963
    21-未来技术：962
    22-创新创业：？
    23-马克思：964
    24-心理学：968
    25-人工智能：969
    26-纳米：970
    27-艺术：971
    TY-体育：946
    2.sids为课程id，获得方式可以点击该课程，网址后面的6位数字即为课程id
    3.加入did_xxxxxx:xxxxxx字段, 代表xxxxxx课程选为学位课
    '''

    data_list=[

        {'deptIds':'952','sids':'136055','did_136055':'136055'},#随机过程 学位课       
        {'deptIds':'969','sids':'138246'},#模式识别 
    ]
    url='http://jwxk.ucas.ac.cn/courseManage/saveCourse?s='+query_string_paras

    flag_dict={data['sids']:0 for data in data_list} #0代表未选上
    count=1

    while 1:
        print('=====================Round '+str(count)+'=========================')
        count=count+1
        #判断是否都选成功了
        '''
        flag=1
        for i in flag_dict.values():
            flag=flag*i
        if flag==1:
            break
        '''
        if not data_list:   #选课列表为空代表都选成功
            print flag_dict #打印出flags验证
            break
        #选课
        for data in data_list:
            try:
                resp=conn.post(url=url,data=data,timeout=3)
            except:
                continue

            error_reg=re.compile(u'冲突')
            success_reg=re.compile(u'成功')

            if success_reg.search(resp.text):
                flag_dict[data['sids']]=1 #将这一门课的flag置1
                data_list.remove(data)    #从列表中删除这一门课
                print (data['sids']+' 选课成功！')

            elif error_reg.search(resp.text):
                conflict_reg=re.compile(u'课程名称为(.+?)，')
                conflict=conflict_reg.findall(resp.text)
                conflict_course=conflict[0]
                print (conflict_course.encode('utf-8')+'，选课失败！')

            else:
                print (data['sids']+' 课程已选满，选课失败！等待退选...')

        time.sleep(1)


