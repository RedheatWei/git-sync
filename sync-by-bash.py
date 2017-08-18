#!/usr/bin/env python
#_*_ coding:utf-8 _*_
'''
Created on '2017/8/17 10:40'
Email: qjyyn@qq.com
@author: Redheat
'''
import  urllib,urllib2,json,os,shutil,sys,time
import xml.dom.minidom
from gittle import Gittle
from commands import getstatusoutput

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
        if textmod:
            textmod = urllib.urlencode(textmod)
            # url = '%s%s%s' % (url, '?', textmod)
        req = urllib2.Request(url=url,headers=header_dict)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
        response = opener.open(req,textmod)
        # res = urllib2.urlopen(req)
        res = response.read()
        return json.loads(res)
class SyncFromRemote(object):
    def __init__(self,private_token,url="10.100.218.203",):
        # self.group = group
        # self.project = project
        self.url_groups = "http://%s/api/v3/groups" % url
        self.url_projects = "http://%s/api/v3/projects" % url
        self.http_request = HttpRequest()
        self.header_dict = {"PRIVATE-TOKEN":private_token}
        self.local_save_path = "/data/mirror_remote"
        # self.remote_git_host = remote_git_host
        self.local_git_host = "10.100.218.203"
    def down_remote_mirror(self,group_name,project_name,remote_git_host):
        local_group_save_path = os.path.join(self.local_save_path,group_name)
        self._mkdir_safe(local_group_save_path)
        local_project_save_path = os.path.join(local_group_save_path,project_name)+".git"
        if os.path.exists(local_project_save_path):
            cmd = "cd %s;git remote update" % local_project_save_path
            print cmd
            stat =  getstatusoutput(cmd)
            print "UPDATE:"+stat[1]
            if stat[0] !=0:
                shutil.rmtree(local_project_save_path)
            else:
                return stat[0]
        cmd = "cd %s;git clone --mirror git@%s:%s/%s.git" % (local_group_save_path,remote_git_host,group_name,project_name)
        print cmd
        stat = getstatusoutput(cmd)
        print "CLONE:"+stat[1]
        return stat[0]
    def push_mirror_to_local(self,group_name,project_name,remote_git_host):
        local_project_save_path = os.path.join(self.local_save_path,group_name,project_name)+".git"
        self._create_project(group_name,project_name)
        if not os.path.exists(local_project_save_path):
            self.down_remote_mirror(group_name,project_name,remote_git_host)
        # cmd = ["cd", local_project_save_path, ";","git push --mirror git@%s:%s/%s.git" % (self.local_git_host, group_name, project_name)]
        cmd = "cd %s;git push --mirror git@%s:%s/%s.git" % (local_project_save_path,self.local_git_host, group_name, project_name)
        print cmd
        print "PUSH:"+getstatusoutput(cmd)[1]
        # shell = subprocess.Popen(cmd, subprocess.PIPE)
        # shell.wait()

    def update_mirror(self,group_name,project_name,remote_git_host):
        if self.down_remote_mirror(group_name, project_name,remote_git_host)==0:
            self.push_mirror_to_local(group_name,project_name,remote_git_host)
    def _create_project(self, group_name, project_name):
        group_id = self._create_group(group_name)
        project_id = self._check_project_exists(group_id, project_name)
        if project_id == 0:
            textmod = {"name": project_name, "namespace_id": group_id}
            project = self.http_request.post_request(self.url_projects, textmod, self.header_dict)
            if project['id']:
                return project['id']
            else:
                print "project %s create error,please check." % project_name
                sys.exit(1)
        return project_id
    def _create_group(self, group_name):
        group_id = self._check_group_exists(group_name)
        if group_id == 0:
            textmod = {"name": group_name, "path": group_name,"description":group_name}
            group = self.http_request.post_request(self.url_groups, textmod, self.header_dict)
            if group[0]['id']:
                return group[0]['id']
            else:
                print "group %s create error,please check." % group_name
                sys.exit(1)
        return group_id
    def _get_all_group(self):
        groups = self.http_request.get_request(self.url_groups,header_dict=self.header_dict)
        return groups
    def _check_group_exists(self,group_name):
        groups = self._get_all_group()
        for group in groups:
            if group['name'] == group_name:
                return group['id']
        return 0
    def _check_project_exists(self,group_id,project_name):
        textmod = {"search":project_name}
        projects = self.http_request.get_request(self.url_groups+"/"+str(group_id)+"/projects",textmod,header_dict=self.header_dict)

        for project in projects:
            if project['name'] == project_name:
                return project['id']
        return 0
    def _mkdir_safe(self,path):
        if path and not (os.path.exists(path)):
            os.makedirs(path)
        return path

class GetGroupAndProject(object):
    def __init__(self,file_name,repo="git@10.240.205.131:thinkcloud_ci/manifests.git"):
        self.repo = repo
        self.file_name = file_name
        self.sync_tmp_file = "/tmp/sync_file"  # 远程仓库manifests临时存放位置
        if not os.path.exists(self.sync_tmp_file):
            os.makedirs(self.sync_tmp_file)
    def _get_name(self):
        try:
            if os.path.exists(self.sync_tmp_file):
                shutil.rmtree(self.sync_tmp_file)
            Gittle.clone(self.repo, self.sync_tmp_file)
        except Exception, e:
            print e
            sys.exit(1)
        else:
            print "clone %s to %s successfully!" % (self.repo, self.sync_tmp_file)
            return xml.dom.minidom.parse(os.path.join(self.sync_tmp_file, self.file_name))
    def get_xml_value(self):
        config_obj = self._get_name()
        doc = config_obj.documentElement
        default_remote = doc.getElementsByTagName("default")[0].getAttribute("remote")
        remote_objs = doc.getElementsByTagName("remote")
        project_objs = doc.getElementsByTagName("project")
        xml_dict = {}
        for remote in remote_objs:
            xml_dict[remote.getAttribute('name')] = {}
            xml_dict[remote.getAttribute('name')]["fetch"] = remote.getAttribute('fetch')
            xml_dict[remote.getAttribute('name')]["review"] = remote.getAttribute('review')
            xml_dict[remote.getAttribute('name')]["project"] = []
        for project in project_objs:
            project_name = project.getAttribute("name")
            project_remote = project.getAttribute('remote')
            if project_remote:
                xml_dict[project_remote]['project'].append(project_name)
            else:
                xml_dict[default_remote]['project'].append(project_name)
        return xml_dict

get_config = GetGroupAndProject(sys.argv[1])
config = get_config.get_xml_value()
sync = SyncFromRemote("vXb3ysPaQ6naPUF9z-FM")
for remote in config:
    group_name = config[remote]["fetch"].split("/")[-1]
    project_fetch = config[remote]["fetch"].split("@")[-1].split("/")[0]
    for project_name in config[remote]["project"]:
        if sync.down_remote_mirror(group_name,project_name,project_fetch) ==0:
            sync.push_mirror_to_local(group_name,project_name,project_fetch)
        sync.update_mirror(group_name,project_name,project_fetch)
        time.sleep(5)



