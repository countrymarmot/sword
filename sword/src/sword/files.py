'''
Created on Sep 18, 2013

@author: mzfa
'''
import fnmatch
import os
import os.path

def get_xml_files(Path, folder_num):
    try:
        for folder in __walk_dir(Path, folder_num):
            for f in __xmlog_in_folder(folder):
                yield f
    except Exception, e:
        print "Error: " + str(e) 
        
def __walk_dir(rootPath, num):
    n = 1
    flist = os.listdir(rootPath)
    flist.reverse()
#     if num>len(flist):
#         num = len(flist)
#     flist = flist[0:num]
#     folders = []
#     for d in flist:
#         folders.append(os.path.join(rootPath, d))
#     return folders
    for d in flist:
        path = os.path.join(rootPath, d)
        if os.path.isdir(path):
            if n <= num:
                yield path
                n = n + 1
                
def __xmlog_in_folder(folder):
    pattern = '*.xml'
    for root, dirs, files in os.walk(folder):
        for filename in fnmatch.filter(files, pattern):
            yield os.path.join(root, filename)
    
if __name__ == "__main__":
    rootPath = 'D:\TestLogForDev'
    n = 0
    for i in get_xml_files(rootPath, 1):
        print str(n) + ":    ",
        print i
        n = n + 1
