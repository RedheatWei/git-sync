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

gitlab_mirrors_path = "/root/gitlab-mirrors"
add_gitlab_mirrors_name = "add_mirror.sh"

class GetConfigFromRemote(object):
    def __init__(self,sync_file_project=None,sync_file_branch=None,sync_tmp_file=None):
        if sync_file_project == None:
            self.sync_file_project = "git@10.240.205.131:thinkcloud_ci/manifests.git"
        else:
            self.sync_file_project = sync_file_project
        if sync_file_branch == None:
            self.sync_file_branch = "thinkcloud_ci_master.xml"
        else:
            self.sync_file_branch = sync_file_branch
        if sync_tmp_file == None:
            self.sync_tmp_file = "/tmp/sync_file"
        else:
            self.sync_tmp_file = sync_tmp_file

    # 下载 manifests
    def clone_sync_file(self):
        try:
            if os.path.exists(self.sync_tmp_file):
                shutil.rmtree(self.sync_tmp_file)
            Gittle.clone(self.sync_file_project, self.sync_tmp_file)
        except Exception, e:
            print e
            sys.exit(1)
        else:
            print "clone %s to %s successfully!" % (self.sync_file_project, self.sync_tmp_file)
            return xml.dom.minidom.parse(os.path.join(self.sync_tmp_file, self.sync_file_branch))

    # 获取 xml配置文件
    def get_xml_value(self, tagName, attribute=None):
        config_obj = self.clone_sync_file()
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
            return value

#将远程代码同步到本地
def add_remote_repo():
    getConfig = GetConfigFromRemote()
    git_project = getConfig.get_xml_value("remote", "fetch")
    project = getConfig.get_xml_value("project")
    add_script = os.path.join(gitlab_mirrors_path,"add_mirror.sh")
    git_url = git_project.split("//")[-1].replace("/", ":")
    for name in project:
        path = project[name]
        remote_path_repo = git_url + "/" + path + ".git"
        child1 = subprocess.Popen(["/bin/bash",add_script,"--git","--project-name",name,"--mirror",remote_path_repo,"/",path,".git"], stdout=subprocess.PIPE)
        child1.wait()

add_remote_repo()