#!/usr/bin/env python
#_*_ coding:utf-8 _*_
'''
Created on '2017/8/14 15:33'
Email: qjyyn@qq.com
@author: Redheat
'''
import sys,os,shutil
import xml.dom.minidom
import subprocess

from gittle import Gittle
from commands import getstatusoutput

sync_file_project = "git@10.240.205.131:thinkcloud_ci/manifests.git"
sync_file_branch = "thinkcloud_ci_master.xml"
sync_tmp_file = "/tmp/sync_file"

remote_to_save_repo = "/data/shanghai_thinkcloud_ci_test/thinkcloud_ci"

gitlab_mirrors_path = "/root/gitlab-mirrors"
add_gitlab_mirrors_name = "add_mirror.sh"

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

#将远程代码同步到本地
def add_remote_repo(config):
    git_project = get_xml_value(config, "remote", "fetch")
    project = get_xml_value(config, "project")
    mkdir_safe(remote_to_save_repo)
    add_script = os.path.join(gitlab_mirrors_path,"add_mirror.sh")
    git_url = git_project.split("//")[-1].replace("/", ":")
    for name in project:
        path = project[name]
        remote_path_repo = git_url + "/" + path + ".git"
        child1 = subprocess.Popen(["/bin/bash",add_script,"--git","--project-name",name,"--mirror",remote_path_repo,"/",path,".git"], stdout=subprocess.PIPE)
        # cmd = "/bin/bash %s --git --project-name %s --mirror %s/%s.git" % (add_script,name,remote_path_repo,path)
        # getstatusoutput(cmd)
        print child1.stdout.readlines()

    # branch = get_xml_value(config, "default", "revision")
    # remote = get_xml_value(config, "default", "remote")

config = clone_sync_file()
add_remote_repo(config)