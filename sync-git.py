#!/usr/bin/env python
#_*_ coding:utf-8 _*_
'''
Created on '2017/8/14 9:58'
Email: qjyyn@qq.com
@author: Redheat
'''
# import sys
# import urllib2
import sys,os,shutil
import xml.dom.minidom
from gittle import Gittle

sync_file_project = "git@10.240.205.131:thinkcloud_ci/manifests.git"
sync_file_branch = "thinkcloud_ci_master.xml"
sync_tmp_file = "/tmp/sync_file"

def clone_sync_file():
    try:
        if os.path.exists(sync_tmp_file):
            shutil.rmtree(sync_tmp_file)
        Gittle.clone(sync_file_project, sync_tmp_file)
    except Exception,e:
        print e
        sys.exit(1)
    else:
        print "clone %s to %s successfully!" % (sync_file_project,sync_tmp_file)
        return xml.dom.minidom.parse(os.path.join(sync_tmp_file,sync_file_branch))

print  clone_sync_file()

