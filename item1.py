#!/usr/bin/python
# -*- coding: UTF-8 -*-
 
"""
@author: zhulin.lian

功能：对目录下的所有图片文件，按拍摄时间重新归档
用法：将脚本和照片放于同一目录，双击运行脚本即可

"""
from datetime import datetime
from pathlib import Path

def removeEmptyDirectories(empty_dir, counts = 0):
    for subdir in Path(empty_dir).iterdir():
        counts += 1
        if subdir.is_dir() and removeEmptyDirectories(subdir) == 0:
            print('Removing directory', subdir)
            subdir.rmdir()
            counts -= 1 #

    return counts
        
if __name__ == '__main__':
    removeEmptyDirectories(r'D:\temp')
    pass
