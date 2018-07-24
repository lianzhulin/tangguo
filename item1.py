#!/usr/bin/python
# -*- coding: UTF-8 -*-
 
"""
@author: zhulin.lian

功能：对目录下的所有图片文件，按拍摄时间重新归档
用法：将脚本和照片放于同一目录，双击运行脚本即可

"""
import sys, re, builtins, exifread
import filecmp
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
            subdir.rmdir() #Remove this directory. The directory must be empty.
            counts -= 1 #

    return counts

def getDatetimeFromParent(img_file):
    dir_dt, is_assigned, dir_comments = None, False, None
    #print(img_file.parent.name)
    m = re.match(r'(\d{8})([@-]*)(.*)', img_file.parent.name)
    if m:
        #print(m.groups())
        dir_dt = datetime.strptime(m.group(1)[:8], '%Y%m%d')
        dir_comments = m.group(3).strip()
        is_assigned = not not m.group(2)
        #print('dir dt', dir_dt)
    return dir_dt, dir_comments, is_assigned

def getDatetimeFromName(img_file):
    name_dt = None
    m = re.match(r'\D*(20\d{6})', img_file.name)
    if m:
        name_dt = datetime.strptime(m.group(1)[:8], '%Y%m%d')
        #print('name dt', name_dt)
    return name_dt

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
                if str(v) not in ('0000:00:00 00:00:00', ):
                    print((t, v))
                #break
    #print(Path(img_file).name, img_dt)
    return img_dt, getDatetimeFromName(img_file), getDatetimeFromParent(img_file)

print = _myprint

class Groups():
    def __init__(self, src_dir):
        self.src_dir = Path(src_dir)
        self.new_dir = self.home_dir = Path(Path(__file__).resolve().anchor).joinpath(datetime.now().strftime('%Y%m%d'))
        self.succ_cnt, self.fail_cnt = 0, 0
        self.fail_not_match_cnt, self.succ_force_assigned_cnt = 0, 0
        self.succ_duplicated_cnt, self.fail_conflict_cnt = 0, 0
        self.FAILURE_FILES = []
        self.min_dt = datetime.max
        self.max_dt = datetime.min
        return

    def build_all(self):
        print('\n')
        for f in self.src_dir.glob('**/*.jpg'):
            print('\r', end='')    #Carriage return
            print('Processing', f.relative_to(self.src_dir), '...', end='')
            img_dt, name_dt, (dir_dt, dir_comments, is_assigned) = getDatetimeFromImage(f)
            #print('R/Image', img_dt, name_dt, (dir_dt, dir_comments, is_assigned))
            if not img_dt:
                img_dt = name_dt

            if not img_dt and not is_assigned:
                self.fail_cnt += 1
                self.FAILURE_FILES.append((f.resolve(), img_dt, name_dt, (dir_dt, dir_comments, is_assigned)))
            elif img_dt and dir_dt and (img_dt - dir_dt).days not in range(-2, 3) and not is_assigned:
                self.fail_not_match_cnt += 1
                self.fail_cnt += 1
                self.FAILURE_FILES.append((f.resolve(), img_dt, name_dt, (dir_dt, dir_comments, is_assigned)))
            else:
                if is_assigned: #force
                    img_dt = dir_dt
                    self.succ_force_assigned_cnt += 1
                    dir_comments = '@' + dir_comments

                if img_dt < self.min_dt:
                    self.min_dt = img_dt
                if img_dt > self.max_dt:
                    self.max_dt = img_dt

                self.new_dir = self.home_dir.joinpath('{}'.format(img_dt.year), img_dt.strftime('%Y%m%d') + dir_comments)
                if not self.new_dir.is_dir():
                    self.new_dir.mkdir(parents=True)

                '''2. Move file to new directory'''
                new_file = self.new_dir.joinpath(f.name)
                if new_file == f: #is the same files, do nothing
                    #self.succ_cnt += 1
                    pass
                elif not new_file.is_file():
                    f.rename(new_file) #be careful
                    self.succ_cnt += 1
                elif filecmp.cmp(f, new_file):
                    self.succ_duplicated_cnt += 1
                    f.unlink() #unlink old file
                else:
                    self.fail_conflict_cnt += 1
                    self.fail_cnt += 1
                    self.FAILURE_FILES.append((f.resolve(), img_dt, name_dt, (dir_dt, dir_comments, is_assigned)))
                    pass

            print('S({0}) F({1}) '.format(self.succ_cnt, self.fail_cnt), end='')
            if self.succ_force_assigned_cnt or self.fail_not_match_cnt or self.succ_duplicated_cnt or self.fail_conflict_cnt:
                print(': A({0}) N({1}) D({2}) C({3})'.format(
                    self.succ_force_assigned_cnt, self.fail_not_match_cnt, self.succ_duplicated_cnt, self.fail_conflict_cnt), end='')
            print('-->', self.new_dir, end='...\t')

        '''Summary the results and remove some unused directories'''    
        print('\n')
        print('Image Datetime range {} .. {}'.format(self.min_dt, self.max_dt))
        if self.FAILURE_FILES:
            print('E/Total ({}) Failure Files:'.format(len(self.FAILURE_FILES)))
            for f in self.FAILURE_FILES:
                print('\t', f)

        res = removeEmptyDirectories(self.src_dir)
        if res == 0: #Remove main directory. The directory must be empty.
            self.src_dir.rmdir()
        return

if __name__ == '__main__':
    print(sys.argv)
    #print(removeEmptyDirectories(r'D:\temp'))
    if (len(sys.argv) > 1):
        src_dir = Path(sys.argv[1])
        if (src_dir.is_dir()):
            Groups(src_dir).build_all()
        else:
            print('E/Not found directory', src_dir)
    pass
