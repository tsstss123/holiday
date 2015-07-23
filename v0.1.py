#!/usr/bin/env python
# -*- coding:utf-8 -*-

import urllib
import urllib2
import cookielib
from lxml import etree
import string
import codecs
import json
try:
    import cPickle as pickle
except ImportError:
    import pickle


__author__ = 'ZhuZichen'


__usr = None
__pwd = None

__ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.130 S' \
       'afari/537.36'

flag = False

cookie = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))


class gradetable(object):
    def __init__(self):
        self.len = 0
        self.coursename = []
        self.grade = []
        self.gpa = []
        self.xuefen = []
        self.gpamark = 0

    def addgrade(self, coursename, grade, gpa, xuefen):
        self.coursename.append(coursename)
        self.grade.append(grade)
        self.gpa.append(gpa)
        self.xuefen.append(xuefen)
        self.len += 1

    def getstringlen(self, s):
        tmp = 0
        for i in s:
            if i >= u'\u4e00' and i <= u'\u9fa5':
                tmp = tmp + 2
            else:
                tmp = tmp + 1
        return tmp

    def getlen(self, table):
        l = 0
        for i in table:
            if self.getstringlen(i) > l:
                l = self.getstringlen(i)
        return l

    def calcgpa(self):
        totalgpa = 0
        for i in self.xuefen:
            totalgpa += string.atof(i)

        for i in range(self.len):
            self.gpamark += ((string.atof(self.gpa[i]) * string.atof(self.xuefen[i])) / string.atof(totalgpa))

    def printgradetable(self):

        for i in range(self.len):
            if string.atof(self.grade[i]) < 60:
                self.coursename[i] = 'X' + self.coursename[i]
            else:
                self.coursename[i] = ' ' + self.coursename[i]

        coursenamelen = self.getlen(self.coursename)
        gradelen = self.getlen(self.grade)
        coursename = self.coursename
        grade = self.grade
        gpa = self.gpa

        for i in range(len(coursename)):
            for j in range(coursenamelen - self.getstringlen(coursename[i])):
                coursename[i] = coursename[i] + ' '

        for i in range(len(grade)):
            for j in range(gradelen - self.getstringlen(grade[i])):
                grade[i] = grade[i] + ' '

        self.calcgpa()
        print '\n\n--------\n总课程数: %s\n--------' % (self.len)
        for i in range(self.len):
            print '%s\t%s\t%s' % (coursename[i], grade[i], gpa[i])
        print '--------\nGPA: %.2f\n--------\n\n' % (self.gpamark)


def uis_cert():
    # --------get session--------
    url_uis_get_session = 'https://uis.uestc.edu.cn/amserver/UI/Login?goto=http%3A%2F%2Fportal.uestc.edu.cn%2Flogin.p' \
                          'ortal'
    head_uis_get_session = {'Host': 'uis.uestc.edu.cn',
                            'User-Agent': __ua,
                            'Connection': 'keep-alive',
                            'DNT': '1',
                            'Referer': 'http://portal.uestc.edu.cn/'}
    req_uis_get_session = urllib2.Request(url=url_uis_get_session,
                                          headers=head_uis_get_session)
    cookie.add_cookie_header(request=req_uis_get_session)
    try:
        opener.open(req_uis_get_session)
    except urllib2.HTTPError, e:
        print e.code
    except urllib2.URLError, e:
        print e.reason

    # --------post cert data--------
    url_uis_post_data = 'https://uis.uestc.edu.cn/amserver/UI/Login'
    head_uis_post_data = {'Host': 'uis.uestc.edu.cn',
                          'User-Agent': __ua,
                          'Connection': 'keep-alive',
                          'Cache-Control': 'max-age=0',
                          'Origin': 'https://uis.uestc.edu.cn',
                          'Content-Type': 'application/x-www-form-urlencoded',
                          'DNT': '1',
                          'Referer': 'https://uis.uestc.edu.cn/amserver/UI/Login?goto=http%3A%2F%2Fportal.uestc.edu.c'
                                     'n%2Flogin.portal'}
    data_uis_post_data = {'IDToken0': '',
                          'IDToken1': __usr,
                          'IDToken2': __pwd,
                          'IDButton': 'Submit',
                          'goto': 'aHR0cDovL3BvcnRhbC51ZXN0Yy5lZHUuY24vbG9naW4ucG9ydGFs',
                          'encoded': 'true',
                          'gx_charset': 'UTF-8'}
    data_uis_post_data_en = urllib.urlencode(query=data_uis_post_data)
    req_uis_post_data = urllib2.Request(url=url_uis_post_data,
                                        headers=head_uis_post_data,
                                        data=data_uis_post_data_en)
    cookie.add_cookie_header(request=req_uis_post_data)
    req_uis_post_data.add_header(key='Contant-Length',
                                 val=str(len(data_uis_post_data_en)))
    try:
        opener.open(req_uis_post_data)
    except urllib2.HTTPError, e:
        if e.code == 404:
            global flag
            flag = True
    except urllib2.URLError, e:
        print e.reason

    # --------portal login--------
    url_portal_login = 'http://portal.uestc.edu.cn/login.portal'
    head_portal_login = {'Host': 'portal.uestc.edu.cn',
                         'User-Agent': __ua,
                         'Cache-Control': 'max-age=0',
                         'DNT': '1'}
    req_portal_login = urllib2.Request(url=url_portal_login,
                                       headers=head_portal_login)
    cookie.add_cookie_header(request=req_portal_login)
    try:
        opener.open(req_portal_login)
    except urllib2.HTTPError, e:
        print e.code
    except urllib2.URLError, e:
        print e.reason

def inputusrpwd():
    global __usr
    global __pwd
    __usr = raw_input('学号: ')
    __pwd = raw_input('密码: ')

def eams_grade(semesterid='63'):
    # --------eams home--------
    url_eams_home = 'http://eams.uestc.edu.cn/eams/home.action'
    head_eams_home = {'Host': 'eams.uestc.edu.cn',
                      'User-Agent': __ua,
                      'DNT': '1',
                      'Referer': 'http://eams.uestc.edu.cn/eams/'}
    req_eams_home = urllib2.Request(url=url_eams_home,
                                    headers=head_eams_home)
    cookie.add_cookie_header(request=req_eams_home)
    try:
        opener.open(req_eams_home)
    except urllib2.HTTPError, e:
        print e.code
    except urllib2.URLError, e:
        print e.reason

    # --------eams get grade--------
    url_eams_grade = 'http://eams.uestc.edu.cn/eams/teach/grade/course/person!search.action'
    head_eams_grade = {'Host': 'eams.uestc.edu.cn',
                       'X-Requested-With': 'XMLHttpRequest',
                       'User-Agent': __ua,
                       'DNT': '1',
                       'Referer': 'http://eams.uestc.edu.cn/eams/teach/grade/course/person.action'}
    params_eams_grade = {'semesterId': semesterid,
                         'projectType': ''}
    params_eams_grade = urllib.urlencode(query=params_eams_grade)
    url_eams_grade = url_eams_grade + '?' + params_eams_grade
    req_eams_grade = urllib2.Request(url=url_eams_grade,
                                     headers=head_eams_grade)
    cookie.add_cookie_header(req_eams_grade)
    try:
        res_eams_grade = opener.open(req_eams_grade)
    except urllib2.HTTPError, e:
        print e.code
    except urllib2.URLError, e:
        print e.reason
    # --------deal with lxml--------
    html = res_eams_grade.read().decode(encoding='utf-8')

    root = etree.HTML(text=html)
    path = etree.XPath(
        path=r'/html/body/div/table/tbody/tr[*]/td[4]|/html/body/div/table/tbody/tr[*]/td[9]|/html/body/div/table/tbody/tr[*]/td[10]|/html/body/div/table/tbody/tr[*]/td[6]')
    text = path(root)

    table = gradetable()

    for num in range(0, len(text), 4):
        table.addgrade(coursename=text[num].text.strip(),
                       xuefen=text[num + 1].text.strip(),
                       grade=text[num + 2].text.strip(),
                       gpa=text[num + 3].text.strip())

    table.printgradetable()


if __name__ == '__main__':

    try:
        f = codecs.open(filename='v0.1_config.json', mode='r', encoding='utf-8')
        t = json.load(fp=f, encoding='utf-8')
        __usr = t['usr']
        __pwd = t['pwd']
    except IOError:
        inputusrpwd()
        with codecs.open(filename='v0.1_config.json', mode='w', encoding='utf-8') as f:
            json.dump(obj={'usr': __usr, 'pwd': __pwd}, fp=f)
    finally:
        if f:
            f.close()

    uis_cert()
    eams_grade()

    # 2014_2015_2    63
    # 2014_2015_1    43
    # 2015_2016_1    84
