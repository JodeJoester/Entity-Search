#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 22 15:25:04 2017

@author: jodejoester
"""

import pandas as pd
import json
#数据样例：馒头   食物
filename='entitytag2016.txt'# filename是entity   tag对文件的存放地址
def entity_writer(s_dir,entity_list):
    with open(s_dir,'w',encoding='utf-8') as fn:
        for entity in entity_list:
            fn.write(entity+'\n')
    fn.close()

class entity_find:
    
    def __init__(self,filename):
        self.filename=filename
        self.entity_dict,self.tag_dict=self.start() #初始化entity_dict和tag_dict
    
    def tag_sort(self,filename): #抽取entity,tag对，做成tag_dict{tag:[entity]}和entity_dict
        tag_dict={}
        entity_dict={}
        with open(filename,'r',encoding='utf-8') as fn:
            for line in fn:
                item=line.split()
                if len(item)==2:
                    try:
                        entity_dict[item[0]].append(item[1]) 
                    except KeyError:
                        entity_dict[item[0]]=[item[1]]
                    try:
                        tag_dict[item[1]].append(item[0])
                    except KeyError:
                        tag_dict[item[1]]=[item[0]]
        fn.close()
        return entity_dict,tag_dict
            
    def start(self):
        entity_dict,tag_dict=self.tag_sort(self.filename) #载入entity_dict,tag_dict
        return entity_dict,tag_dict

    def tag_find(self,pos_tags,tag_dict=None,entity_dict=None): #输出结果为DF
        #将默认参数设为已定义的的成员变量
        if tag_dict is None:
            tag_dict=self.tag_dict
        if entity_dict is None:
            entity_dict=self.entity_dict
        #将字符串输入规范为列表
        if type(pos_tags)==str:
            pos_tags=[pos_tags]
        tag_extend={}
        for tag in pos_tags: #对给定的tag,给出tag_dict中的对应entity（直接联系实体）
            if tag not in tag_dict:
                print('"',tag,'"','不存在于文件中')
            for entity in tag_dict[tag]:
                for tag_ext in entity_dict[entity]:#通过直接联系实体查询外部标签 
                    if tag_ext not in pos_tags:#如果每次通过直接联系实体查询到某一标签，该标签对应freq++{外部标签:freq}
                        tag_extend.setdefault(tag_ext,0)
                        tag_extend[tag_ext]+=1
        for tag_ext in tag_extend:#所有查询到的外部标签中：count=0，freq是tag_ext的出现频率
            count=0
            freq=tag_extend[tag_ext]
            for entity in tag_dict[tag_ext]:#通过外部标签查找外部实体，如果外部实体对应标签出现在原始标签集中，该标签对应count++
                for tag_ote in entity_dict[entity]:
                    if tag_ote in pos_tags:
                        count+=1
                        
                        break
            prop=count/len(tag_dict[tag_ext])#prop:count/外部标签对应实体总数
            tag_extend.update({tag_ext:[freq,prop]})
        return pd.DataFrame(data=tag_extend,index=['frequency','proportion']).T

    def tag_reduce(self,tag_list,tag_dict=None,entity_dict=None,neg_tags=[],neg_entity=[]):
        if tag_dict is None:
            tag_dict=self.tag_dict
        if entity_dict is None:
            entity_dict=self.entity_dict
        #如果给出负实体，则拓展负实体的相关概念作为负概念
        neg_tags=set(neg_tags)
        neg_entity=set(neg_tags)
        if len(neg_entity)==0:
            pass
        else:
            for entity in neg_entity:
                neg_tags=neg_tags.union(entity_dict[entity])
        #对于负概念的处理：从正概念当中删除负概念
        if len(neg_tags)==0:
            pass
        else:
            for tag in neg_tags:
                if tag in tag_list:
                    tag_list.remove(tag)

    #利用负概念和负实体剪除搜得实体，剪除条件：实体中有负概念且没有核心概念
    def entity_reduce(self,entity_list,core_tag,tag_dict=None,entity_dict=None,neg_tags=[],neg_entity=[]):
        if tag_dict is None:
            tag_dict=self.tag_dict
        if entity_dict is None:
            entity_dict=self.entity_dict
        if not neg_entity: #在entity_list中减去负实体
            pass
        else:
            for entity in neg_entity:
                if entity in entity_list:
                    entity_list.remove(entity)
        #减去相关tag中有负概念的entity且没有核心概念的实体
        deleted=[]
        if type(core_tag)==str:
            core_tag=set([core_tag])
        for entity in entity_list:
            flag=0
            for tag in entity_dict[entity]:
                if tag in neg_tags:
                    flag+=1
                if tag in core_tag:
                    flag=0
                    break
            if flag>0:
                entity_list.remove(entity)
                deleted.append(entity)
                continue
        return deleted
                
        
                
            
    def tag_writer(self,tags,save_dir):
        with open(save_dir,'w') as sd:
            for tag in tags:
                sd.write(str(tag[0])+'\t'+str(tag[1])+'\n')
        sd.close()
        return 0

    def tag_reader(self,read_dir):
        items=[]
        with open(read_dir) as rd:
            for line in rd:
                item=tuple(line.split())
                items.append(item)
        return items


    def dict_writer(self,dictObj,savename):
        jsObj=json.dumps(dictObj)
        fileObject=open(savename,'w')
        fileObject.write(jsObj)
        fileObject.close()

    def entity_search(self,taglist,tag_dict=None):
        if tag_dict is None:
            tag_dict=self.tag_dict
        entity_list=set()
        if type(taglist)==str:
            taglist=[taglist]
        for tag in taglist:
            for entity in tag_dict[tag]:
                entity_list.add(entity)
        return list(entity_list)


    def entity_writer(self,s_dir,entity_list):
        with open(s_dir,'w',encoding='utf-8') as fn:
            for entity in entity_list:
                fn.write(entity+'\n')
        fn.close()

    def binary_cut_search(self,full_tags,core_tag,entity_dict=None,tag_dict=None,pos_threshold=0.32,neg_threshold=0.1,freq_threshold=50,delete=False):  #自动搜索方法，flag=0时不进行负实体删除
        if tag_dict is None:
            tag_dict=self.tag_dict
        if entity_dict is None:
            entity_dict=self.entity_dict
    
        pos_tags=full_tags[full_tags['proportion']>pos_threshold]
        neg_tags=full_tags[full_tags['proportion']<neg_threshold]
        neg_tags=neg_tags[neg_tags['frequency']/neg_tags['proportion']<freq_threshold]
        neg_tags=list(neg_tags.index)
        pos_tags=list(pos_tags.index)
        pos_entity=self.entity_search(pos_tags,tag_dict)
        core_entity=self.entity_search(tag_dict=tag_dict,taglist=core_tag)
        deleted=[]
        if delete:
            deleted=self.entity_reduce(pos_entity,core_tag,tag_dict=tag_dict,entity_dict=entity_dict,neg_tags=neg_tags,neg_entity=[])
        pos_entity=list(set(pos_entity).union(set(core_entity)))
        return pos_entity,deleted

    def auto_search(self,core_tag,entity_dict=None,tag_dict=None,pos_threshold=0.32,neg_threshold=0.1,freq_threshold=30,delete=False):
        if tag_dict is None:
            tag_dict=self.tag_dict
        if entity_dict is None:
            entity_dict=self.entity_dict
        full_tags=self.tag_find(pos_tags=core_tag,tag_dict=tag_dict,entity_dict=entity_dict)
        pos_entity,deleted=self.binary_cut_search(entity_dict=entity_dict,tag_dict=tag_dict,full_tags=full_tags,core_tag=core_tag,pos_threshold=pos_threshold,neg_threshold=neg_threshold,freq_threshold=freq_threshold,delete=delete)
        return pos_entity,deleted

    def mannual_search(self,core_tag,neg_tags,entity_dict=None,tag_dict=None,pos_threshold=0.32):
        if tag_dict is None:
            tag_dict=self.tag_dict
        if entity_dict is None:
            entity_dict=self.entity_dict
        full_tags=self.tag_find(pos_tags=core_tag,tag_dict=tag_dict,entity_dict=entity_dict)
        pos_tags=full_tags[full_tags['proportion']>pos_threshold]
        pos_tags=list(pos_tags.index)
        core_entity=self.entity_search(tag_dict=tag_dict,taglist=core_tag)
        pos_entity=self.entity_search(pos_tags,tag_dict)
        deleted=self.entity_reduce(pos_entity,core_tag,tag_dict=tag_dict,entity_dict=entity_dict,neg_tags=neg_tags,neg_entity=[])
        pos_entity=list(set(pos_entity).union(set(core_entity)))
        return pos_entity,deleted

    def search_and_write(self,core_tag,entity_dict=None,tag_dict=None,pos_threshold=0.32,neg_threshold=0.1,freq_threshold=30,delete=False):
        if tag_dict is None:
            tag_dict=self.tag_dict
        if entity_dict is None:
            entity_dict=self.entity_dict
        pos_entity,deleted=self.auto_search(core_tag=core_tag,entity_dict=entity_dict,tag_dict=tag_dict,pos_threshold=pos_threshold,neg_threshold=neg_threshold,freq_threshold=freq_threshold,delete=delete)
        if type(core_tag)==list:
            core_tag=core_tag[0]
        self.entity_writer(core_tag+'实体.txt',pos_entity)
        return pos_entity,deleted
    
    def multi_tag_writers(self,core_tags,pos_threshold=0.32,neg_threshold=0.1,freq_threshold=30,delete=False):
        deleted=[]
        for core_tag in core_tags:
            deleted.append(self.search_and_write(core_tag,pos_threshold=pos_threshold,neg_threshold=neg_threshold,freq_threshold=freq_threshold,delete=delete)[1])
        return deleted



'''
使用方法：
from entity_search.py import *
filename="entity    tag对文件的存放地址"
start() #初始化entity_dict和dict_dict

1.利用核心概念（如“金融”）进行搜索并自动将结果存入“金融实体.txt”,不使用负概念进行筛选则flag=0(默认),进行自动筛选则flag=1：
pos_entity,deleted=search_and_write(core_tag='金融',flag=0)

2.利用核心概念（如“医疗”），并给定手动筛选出的严格负概念列表(neg_tags)：
pos_entity,deleted=mannual_search(core_tag='医疗',neg_tags=neg_tags)

3.手动将筛选出的实体存成文件，存入s_dir：
entity_writer(s_dir,pos_entity)

4.给出需要搜索的核心概念列表core_tags(如['金融','教育','医疗'])，对其中的每个核心概念进行搜索并自动存成相应文件：
multi_tag_writers(core_tags)
'''


