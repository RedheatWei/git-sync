#!/usr/bin/env python
#_*_ coding:utf-8 _*_
'''
Created on '2017/8/14 15:33'
Email: qjyyn@qq.com
@author: Redheat
'''
import sys,os,shutil
import xml.dom.minidom
import subprocess,time
from gittle import Gittle

sync_file_project = "git@10.240.205.131:thinkcloud_ci/manifests.git" #远程仓库manifests
sync_file_branch = "thinkcloud_ci_master.xml"#分支文件
sync_tmp_file = "/tmp/sync_file" #远程仓库manifests临时存放位置

gitlab_mirrors_path = "/root/gitlab-mirrors" #gitlab-mirrors脚本目录
add_gitlab_mirrors_name = "add_mirror.sh"#增加脚本
update_gitlab_mirrors_name = "update_mirror.sh"#更新脚本

local_code_path = "/data/local_thinkcloud_ci"#本地存放代码的主目录
local_code_prefix = "thinkcloud_ci_"#本地存放代码的目录前缀,后面应该加分支名字
local_git_repo = "git@10.100.218.203:thinkcloud_test"#本地git库


#在远程服务器获取配置文件
class GetConfigFromRemote(object):
    def __init__(self,sync_file_project,sync_file_branch,sync_tmp_file):
            self.sync_file_project = sync_file_project
            self.sync_file_branch = sync_file_branch
            self.sync_tmp_file = sync_tmp_file
    # 下载 manifests
    def _clone_sync_file(self):
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
        config_obj = self._clone_sync_file()
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
#创建目录
    def mkdir_safe(path):
        if path and not (os.path.exists(path)):
            os.makedirs(path)
        return path

#同步和更新到本地git库
class RepoSync(object):
    def __init__(self):
       self.getConfig = GetConfigFromRemote(sync_file_project,sync_file_branch,sync_tmp_file)
    # 将远程代码同步到本地
    def add_remote_repo(self):
        git_project = self.getConfig.get_xml_value("remote", "fetch")
        project = self.getConfig.get_xml_value("project")
        add_script = os.path.join(gitlab_mirrors_path, add_gitlab_mirrors_name)
        git_url = git_project.split("//")[-1].replace("/", ":")
        for name in project:
            path = project[name]
            remote_path_repo = git_url + "/" + path + ".git"
            shell = subprocess.Popen(
                ["/bin/bash", add_script, "--git", "--project-name", name, "--mirror", remote_path_repo, "/", path,
                 ".git"], stdout=subprocess.PIPE)
            shell.wait()
    # 更新project
    def update_remote_repo(self):
        project = self.getConfig.get_xml_value("project")
        update_script = os.path.join(gitlab_mirrors_path, update_gitlab_mirrors_name)
        for name in project:
            print name
            child1 = subprocess.Popen(["/bin/bash", update_script, name], stdout=subprocess.PIPE)
            child1.wait()
            time.sleep(10)



class CloneToLocal(object):
    def __init__(self,local_code_path,local_code_prefix):
        self.getConfig = GetConfigFromRemote(sync_file_project,sync_file_branch,sync_tmp_file)
        self.local_code_path = local_code_path
        self.local_code_prefix = local_code_prefix
    def clone_code(self):
        project = self.getConfig.get_xml_value("project")
        revision = self.getConfig.get_xml_value("default","revision")
        # origin = self.getConfig.get_xml_value("default","origin")
        local_path = os.path.join(local_code_path,local_code_prefix)+revision
        self.getConfig.mkdir_safe(local_path)
        for name in project:
            path = project[name]
            local_orgin_path = os.path.join(local_path,path)
            origin_uri = local_git_repo+"/"+name+".git"
            if not os.path.exists(local_orgin_path):
                try:
                    self._clone_local(local_orgin_path,origin_uri,revision)
                except Exception,e:
                    print e
            else:
                try:
                    self._update_local(local_orgin_path,origin_uri)
                except Exception,e:
                    print e
                    shutil.rmtree(local_orgin_path)
                    self._clone_local(local_orgin_path,origin_uri,revision)
    def _clone_local(self,local_orgin_path,origin_uri,revision):
        shell = subprocess.Popen(
            ["git", "clone", "-b", revision, origin_uri, local_orgin_path], stdout=subprocess.PIPE)
        shell.wait()
    def _update_local(self,local_orgin_path,origin_uri):
        repo = Gittle(local_orgin_path, origin_uri=origin_uri)
        repo.pull()

repo_rsyc = RepoSync()
repo_rsyc.add_remote_repo()
repo_rsyc.update_remote_repo()

clone_to_local = CloneToLocal(local_code_path,local_code_prefix)
clone_to_local.clone_code()