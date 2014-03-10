#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''

Extract APIs defined in android.jar

Created on 2014-3-10

@author: Wenjun Hu
'''

import os, sys, subprocess, re

def get_java_tools():
    java_home = os.environ.get('JAVA_HOME')
    if java_home == None:
        print 'JDK not found'
        return None, None
    is_linux = False
    if sys.platform.startswith('linux'):
        is_linux = True

    jar_tool = os.path.join(java_home, 'bin', 'jar' if is_linux else 'jar.exe')
    javap_tool = os.path.join(java_home, 'bin', 'javap' if is_linux else 'javap.exe')
    
    return jar_tool, javap_tool
    
def parse_android_jar(android_jar_path):
    if not os.path.join(android_jar_path):
        print '%s not exists' % android_jar_path
        return
      
    # Get java tools  
    jar_tool, javap_tool = get_java_tools()
    if not os.path.exists(jar_tool):
        print '%s not exists' % jar_tool
        return
    if not os.path.exists(javap_tool):
        print '%s not exists' % javap_tool
        return
    
    # Call jar -tf android.jar to get all the classes
    jar_args = [jar_tool, '-tf', android_jar_path]
    jar_popen = subprocess.Popen(jar_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    classes = jar_popen.communicate()[0]
    class_name_list = []
    if classes:
        class_name_list_tmp = classes.split(os.linesep)
        
        for class_name in class_name_list_tmp:
            if class_name.endswith('.class'):
                class_name_list.append(class_name.replace('.class',''))
    
    # Call javap -bootclasspath android.jar -s class_name 
    method_name_pattern = re.compile('(.+\s){1,}(.+)\(.*\)\s?')
    class_method_map = {}
    for class_name in class_name_list:
        print 'Parse class %s ...' % class_name
        try:
            javap_args = [javap_tool, '-bootclasspath', android_jar_path, class_name]
            javap_popen = subprocess.Popen(javap_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            methods = javap_popen.communicate()[0]
            method_list_tmp = methods.split(os.linesep)
            method_name_set = set([])
            for method_descriptor in method_list_tmp:
                method_descriptor = method_descriptor.strip()
                method_name_found = method_name_pattern.findall(method_descriptor)
                if method_name_found:
                    method_name_set.add(method_name_found[0][1])
            class_method_map[class_name] = list(method_name_set)
        except Exception,ex:
            print ex
            continue
        
    return class_method_map
        

if __name__ == '__main__':
    # Parse APIs   
    class_method_map = parse_android_jar(r'android.jar')
    
    