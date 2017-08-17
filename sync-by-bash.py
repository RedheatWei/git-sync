#!/usr/bin/env python
#_*_ coding:utf-8 _*_
'''
Created on '2017/8/17 10:40'
Email: qjyyn@qq.com
@author: Redheat
'''
import  urllib,urllib2,json
class HttpRequest(object):
    def get_request(self,url,textmod=None,header_dict=None):
        if textmod:
            textmod = urllib.urlencode(textmod)
            url = '%s%s%s' % (url, '?', textmod)
        req = urllib2.Request(url, headers=header_dict)
        # if header_dict:
        #     req = urllib2.Request(url,headers=header_dict)
        # else:
        #     req = urllib2.Request(url)
        res = urllib2.urlopen(req)
        res = res.read()
        return json.loads(res)
    def post_request(self,url,textmod=None,header_dict=None):
        textmod = json.dumps(textmod)
        req = urllib2.Request(url=url, data=textmod,headers=header_dict)
        res = urllib2.urlopen(req)
        res = res.read()
        return json.loads(res)
class SyncFromRemote(object):
    def __init__(self,private_token):
        # self.group = group
        # self.project = project
        self.url = "http://10.100.218.203/api/v3/groups"
        self.http_request = HttpRequest()
        self.private_token = private_token
    def get_all_group(self):
        header_dict = {"PRIVATE-TOKEN":self.private_token}
        groups = self.http_request.get_request(self.url,header_dict=header_dict)
        for i in groups:
            print i

sync = SyncFromRemote("vXb3ysPaQ6naPUF9z-FM")
sync.get_all_group()


