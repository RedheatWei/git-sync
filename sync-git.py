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

remote_to_save_repo = "/data/shanghai_thinkcloud_ci_test/thinkcloud_ci"


def mkdir_safe(path):
    if path and not(os.path.exists(path)):
        os.makedirs(path)
    return path


#下载 manifests
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
#获取 xml配置文件
def get_xml_value(config_obj,tagName,attribute=None):
    doc = config_obj.documentElement
    tag_objs = doc.getElementsByTagName(tagName)
    tag_number = len(tag_objs)
    if tag_number > 1:
        obj_list = {}
        for obj in tag_objs:
            obj_list[obj.getAttribute("name")] = obj.getAttribute("path")
        return obj_list
    else:
        tag_obj = doc.getElementsByTagName(tagName)[0]
        value = tag_obj.getAttribute(attribute)
        return  value

#将远程代码下载到本地
def clone_remote_repo(config):
    git_project = get_xml_value(config, "remote", "fetch")
    # branch = get_xml_value(config, "default", "revision")
    # remote = get_xml_value(config, "default", "remote")
    project = get_xml_value(config, "project")
    # save_path = remote_to_save_repo
    mkdir_safe(remote_to_save_repo)
    for name in project:
        path = project[name]
        project_path = os.path.join(remote_to_save_repo,path)
        "//".split(git_project)[-1].replace("/",":")
        remote_path = git_project+"/"+path+".git"
        if os.path.exists(project_path):
            shutil.rmtree(project_path)
        try:
            print "clone project %s start!" % name
            print  remote_path
            Gittle.clone(remote_path,project_path,bare=True)
        except Exception,e:
            print e
        else:
            print "%s clone to %s successfuly!" % (remote_path,project_path)

config = clone_sync_file()
clone_remote_repo(config)
