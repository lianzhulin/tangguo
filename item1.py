#!/usr/bin/python
# -*- coding: UTF-8 -*-
 
"""
@author: zhulin.lian

功能：对目录下的所有图片文件，按拍摄时间重新归档
用法：将脚本和照片放于同一目录，双击运行脚本即可

"""
import sys, re, builtins, exifread
from datetime import datetime
from pathlib import Path

# ANSI color names.
COLORS = dict(zip('UEIWSRUU', zip(('black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white'), range(30, 38))))
def _myprint(*args, **kwargs):
    if args:
        tag = re.match('([WEISR])/(.*)', str(args[0]))  #startswith some tags
        if tag:
            builtins.print('\033[01;{}m'.format(COLORS[tag.group(1)][1]), end='')
            builtins.print(*args, **kwargs)
            builtins.print('\033[00m', end='') #restore
            return

    builtins.print(*args, **kwargs)
    return
 
def removeEmptyDirectories(empty_dir, counts = 0):
    for subdir in Path(empty_dir).iterdir():
        counts += 1
        if subdir.is_dir() and removeEmptyDirectories(subdir) == 0:
            print('Removing directory', subdir)
            subdir.rmdir()
            counts -= 1 #

    return counts

def getDatetimeFromImage(img_file):
    img_dt = None
    # Open image file for reading (binary mode)
    f = Path(img_file).open('rb')
    # Return Exif tags
    tags = exifread.process_file(f, details=False)
    f.close()
    for t, v in tags.items():
        if re.search('DateTime.*', t):
            try:
                res = datetime.strptime(str(v).strip(), '%Y:%m:%d %H:%M:%S')
                if not img_dt or res < img_dt:
                    img_dt = res
            except ValueError:
                if (str(v) not in '0000:00:00 00:00:00'):
                    print(t, ':', v)
                #break
    #print(Path(img_file).name, img_dt)
    return img_dt

print = _myprint

class Groups():
    def __init__(self, src_dir):
        self.src_dir = Path(src_dir)
        self.succ_cnt = self.fail_cnt = 0
        self.FAILURE_FILES = []
        self.min_dt = datetime.max
        self.max_dt = datetime.min
        return

    def build_all(self):
        print('\n')
        for f in self.src_dir.glob('**/*.jpg'):
            print('\r', end='')    #Carriage return
            print('Processing', f.relative_to(self.src_dir), '...', end='')
            img_dt = getDatetimeFromImage(f)
            if not img_dt:
                self.fail_cnt += 1
                self.FAILURE_FILES.append(f.resolve())
            else:
                self.succ_cnt += 1
                if img_dt < self.min_dt:
                    self.min_dt = img_dt
                if img_dt > self.max_dt:
                    self.max_dt = img_dt
            print('S({0}) F({1}) '.format(self.succ_cnt, self.fail_cnt), end='')


        '''Summary the results and remove some unused directories'''    
        print('\n')
        print('Image Datetime range {} .. {}'.format(self.min_dt, self.max_dt))
        if self.FAILURE_FILES:
            print('E/Total ({}) Failure Files:'.format(len(self.FAILURE_FILES)))
            for f in self.FAILURE_FILES:
                print('\t', f)
        return

if __name__ == '__main__':
    print(sys.argv)
    #print(removeEmptyDirectories(r'D:\temp'))
    if (len(sys.argv) > 1):
        src_dir = Path(sys.argv[1])
        if (src_dir.is_dir()):
            Groups(src_dir).build_all()
        else:
            print('Not found directory', src_dir)
    pass
