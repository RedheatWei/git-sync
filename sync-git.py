#!/usr/bin/env python
#_*_ coding:utf-8 _*_
'''
Created on '2017/8/14 9:58'
Email: qjyyn@qq.com
@author: Redheat
'''
# import sys
# import urllib2
from gittle import Gittle
sync_file_project = "git@10.240.205.131:thinkcloud_ci/manifests.git"
sync_file_branch = "thinkcloud_ci_master.xml"
sync_tmp_file = "/tmp"
repo = Gittle.clone(sync_file_project,sync_tmp_file)
print repo