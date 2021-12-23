#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Copyright (C) 2017 The Open Source Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

'''
@Version:   1.1.1
@author:    weizhijun
@file:      parse_makefile.py
@Created:   2020-05-05 
@mail:      zhijun.wei@ecarx.com.cn
@descripe:  This file is designed to parse kernel makefile for source code file. 
'''

import sys
import re
import os.path

usage = '''usage: parse_makefile.py kernel path and config name'''
config = []

configmatch = re.compile(r"\$\((CONFIG_[\w]+)\)")
dirmatch = re.compile(r"([\w-]+/)[\s]")
filematch = re.compile(r"([\w-]+\.o)[\s]")

file_count = 0

arrays = [
#'arch/arm64/',
'block/',
'crypto/',
'fs/',
'init/',
'ipc/',
'kernel/',
'lib/',
'mm/',
'net/',
'security/',
'sound/',
'usr/',
'drivers/'
]

unknowlines = 0

class MakeFile(object):
    """docstring for MakeFile"""
    def __init__(self, mdir, config):
        super(MakeFile, self).__init__()
        self.mdir = mdir
        self.mconfig = config
        self.makefile = self.mdir + "Makefile"
        self.mfiles = []
        self.mdirs = []
        self.mfilecount = 0
        self.mlines = 0

        self.munknowlines = 0

        self.__mdeep = 0
        self.__mdefine = 1
        self.__mnodefine = 0
        self.__tmpdeep = self.__mdeep


    def __check_config(self, config):
        if (config == False):
            return False

        for item in self.mconfig:
            if config == item:
                #print item, lists
                return True

        return False


    def __match_line_config(self, line):
        tmp = configmatch.findall(line)

        if tmp:
            if (self.__check_config(tmp[0])):
                return 1
            else:
                return 0

        #print line
        return 1


    def __parse_line(self, line):
        if self.__match_line_config(line):
            files = filematch.findall(line)
            dirs = dirmatch.findall(line)

            if files:
                self.mfiles.extend(files)

            if dirs:
                self.mdirs.extend(dirs)

            if files == [] and dirs == []:
                global unknowlines
                self.munknowlines += 1
                unknowlines += 1
                #print unknowlines, line


    def __define_match(self, line):
        if (self.__match_line_config(line)):
            self.__mdefine |= (1 << self.__mdeep)
            return True
        else:
            self.__mdefine &= ~(1 << self.__mdeep)
            if (self.__tmpdeep == 0):
                self.__tmpdeep = self.__mdeep
            return False

    def __define_unmatch(self, line):
        if (self.__match_line_config(line)):
            self.__mdefine &= ~(1 << self.__mdeep)
            if (self.__tmpdeep == 0):
                self.__tmpdeep = self.__mdeep
            return False
        else:
            self.__mdefine |= (1 << self.__mdeep)
            return True


    def __check_ignore_line(self, line):
        line = line.lstrip()
        #return False

        if ('ifeq' == line[:4]):
            self.__mdeep += 1
            self.__define_match(line)
            #return True
        elif ('ifneq' == line[:5]):
            self.__mdeep += 1
            self.__define_unmatch(line)
        
        elif ('else ifeq' == line[:9]):
            if (self.__match_line_config(line)):
                self.__mdefine |= (1 << (self.__mdeep))

            #return True

        elif ('else' == line[:4]):
            if self.__mdefine & (1 << self.__mdeep):
                self.__mdefine &= ~(1 << (self.__mdeep))
            else:
                self.__mdefine |= (1 << (self.__mdeep))

            #return True
        
        elif ('endif' == line[:5]):
            self.__mdefine &= ~(1 << self.__mdeep)
            if self.__mdeep == 0:
                self.__tmpdeep = 0
            else:
                self.__mdeep -= 1
            return True
        else:
            #print line
            pass
            #return True

        #print self.__mdeep, self.__tmpdeep, line
        if (self.__mdeep < self.__tmpdeep):
            #print self.__mdeep, self.__tmpdeep, line
            return False
        elif (self.__mdefine & (1 << self.__mdeep)):
            #print self.__mdeep, line
            return False
        else:
            #print "123", line
            return True


    def __file_check(self, file):
        tmp_line = ''
        for line in self.mlines:
            if line.isspace() or line[0] == '#':
                continue

            if (line[-2] == '\\'):
                tmp_line += line
                continue

            tmp_line += line

            if file in tmp_line:
                if (self.__match_line_config(tmp_line)):
                    #print tmp_line
                    return True
                else:
                    return False

            tmp_line = ''

        return False

    def __line_check(self, line):
        lists = line.split()
        strs = lists[0]

        if (strs == 'obj-y'):
            return True

        if (strs[:12] == 'obj-$(CONFIG'):
            if (self.__check_config(strs[6:-1])):
                return True
            else:
                return False

        if ('-y' in strs):
            file = strs[:-2] + '.o'
            #print file, line
            return self.__file_check(file)

        if ('-$' in strs):
            #print line
            if (self.__match_line_config(line)):
                idx = strs.index('-$')
                file = strs[:idx] + '.o'
                return self.__file_check(file)
            else:
                return False

        if ('-objs' in strs):
            file = strs[:-5] + '.o'
            return self.__file_check(file)

        return False


    def parse_file(self):
        if (os.path.isfile(self.makefile) == False):
            print self.makefile + ' is not exist'
            return None

        with open(self.makefile, 'r') as fp:
            self.mdirs = []
            self.mfiles = []

            filelines = fp.readlines()
            self.mlines = filelines

            tmp_line = ''
            for line in filelines:
                if line.isspace() or line[0] == '#':
                    continue

                if (line[-2] == '\\'):
                    #print line
                    tmp_line += line
                    continue

                tmp_line += line

                if (self.__check_ignore_line(tmp_line)):
                    tmp_line = ''
                    continue

                if self.__line_check(tmp_line) is False:
                    #print tmp_line
                    tmp_line = ''
                    continue 

                print tmp_line
                self.__parse_line(tmp_line)
                tmp_line = ''

            self.mfiles = list(set(self.mfiles))
            self.mfiles.sort()
            self.mdirs = list(set(self.mdirs))
            self.mdirs.sort()


    def get_files(self):
        return self.mfiles


    def get_dirs(self):
        return self.mdirs


    def get_file_count(self):
        if self.mfilecount:
            return self.mfilecount
        else:
            return len(self.mfiles)


    def write_to_file(self, writefile):
        if self.mfiles == []:
            return

        writefile.write("######################### " + self.mdir + "\n")
        for file in self.mfiles:
            tmpfile = self.mdir + file[:-1] + 'c'
            if os.path.exists(tmpfile):
                self.mfilecount += 1
                #writefile.write(file[:-1] + 'c\n')
                writefile.write(tmpfile + '\n')
                os.system('ctags -a ' + tmpfile)
            else:
                #print tmpfile, " not exists"
                pass
        if self.mfilecount:
            writefile.write("######################### " + self.mdir + "  file_count " + str(self.mfilecount) + "\n\n")
            #writefile.write('\n')


def write_files(dir, writefile):
    global config
    global file_count

    makefile = MakeFile(dir, config)
    makefile.parse_file()

    makefile.write_to_file(writefile)
    file_count += makefile.get_file_count()
    dirs = makefile.get_dirs()
    if dirs:
        for it in dirs:
            write_files(dir+it, writefile)


def _Main(argv):

    fw = open('Makefile.txt', 'w')

    caculate = []
    sums = 0
    path_file = argv[0]

    if (os.path.exists(path_file) == False):
        print(usage)
        return

    path = os.path.abspath(os.path.join(os.path.dirname(path_file), "../../../"))
    #print path #os.chdir(path)

    try:
        with open(path_file, 'r') as fp:
            lines = fp.readlines()
            for line in lines:
                if line[0] == '#' or line.isspace():
                    continue

                #print line
                config.append(line.split('=')[0])
                #print config

        os.chdir(path)

        global file_count

        for item in arrays:
            #parse_makefile(item, fw)
            write_files(item, fw)
            sums += file_count
            caculate.append(item + " " + str(file_count) + "\n")
            #print item + " ", file_count
            file_count = 0

    except Exception as e:
        raise e
    finally:
        pass

    for item in caculate:
        fw.write(item)

    fw.write("all file count " + str(sums))
    print "all file count ", sums

    fw.close()


if __name__ == '__main__':
    _Main(sys.argv[1:])
