#!/usr/bin/python
# -*- coding: UTF-8 -*-
 
"""
@author: zhulin.lian

功能：对目录下的所有图片文件，按拍摄时间重新归档
用法：将脚本和照片放于同一目录，双击运行脚本即可

"""
import os, sys, re, builtins, exifread, hashlib
import filecmp, time
from datetime import datetime
from pathlib import Path

VALID_YEARS = range(1997, datetime.now().year + 1)

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
 
def setupHomeDirectory(src_dir):
    if src_dir.parent != src_dir.parent.parent:
        #print(src_dir.parent)
        res = setupHomeDirectory(src_dir.parent)
        if res:
            return res

    m = re.match(r'(\d{4})([~@]+)(.*)', src_dir.name) #2018@balabala
    if m:
        print ('Got home dir', src_dir) #got it
        return src_dir

    return

def removeEmptyDirectories(empty_dir, counts = 0):
    for subdir in Path(empty_dir).iterdir():
        counts += 1
        if subdir.is_dir() and removeEmptyDirectories(subdir) == 0:
            print('W/Removing directory', subdir)
            subdir.rmdir() #Remove this directory. The directory must be empty.
            counts -= 1 #

    return counts

def getDatetimeFromDName(img_file):
    dir_dt, is_assigned, dir_comments = None, False, None
    #print(img_file.name)
    m = re.match(r'(\d{8})([@-]*)(.*)', img_file.name)
    if m:
        #print(m.groups())
        dir_dt = datetime.strptime(m.group(1)[:8], '%Y%m%d')
        dir_comments = m.group(3).strip()
        is_assigned = not not m.group(2)
        #print('dir dt', dir_dt)
    return dir_dt, dir_comments, is_assigned

def getDatetimeFromName(img_file):
    name_dt = None

    'check camera file name pattern, like MA201409290822480045-52-000000000.jpg, 2014-03-15 12.19.07.jpg, PIC_20140531_133012_16A.jpg'
    m = re.match(r'\D*(20\d{2})[-]*(\d{2})[-]*(\d{2})', img_file.name)
    if m:
        name_dt = datetime.strptime(''.join(m.groups()), '%Y%m%d')
        if name_dt.year in VALID_YEARS:
            #print('name dt', name_dt)
            return name_dt

    'check mmexport file name pattern, like mmexport1479703084838.jpg'
    m = re.match(r'\D*(1[345]\d{11})', img_file.name)
    if m:
        name_dt = datetime.fromtimestamp(float(m.group(1))/1e3)
        if name_dt.year in VALID_YEARS:
            #print('name dt', name_dt)
            return name_dt

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
                v2 = str(v).strip()
                res = datetime.fromtimestamp(float(v2)) if v2.isdigit() else datetime.strptime(v2, '%Y:%m:%d %H:%M:%S')
                #print((t, v), res)
                if not img_dt or res < img_dt:
                    img_dt = res
            except ValueError:
                if str(v) not in ('0000:00:00 00:00:00', ):
                    print((t, v))
                #break
    #print(Path(img_file).name, img_dt)
    return img_dt, getDatetimeFromName(img_file), getDatetimeFromDName(img_file.parent)

print = _myprint

class Groups():
    def __init__(self, src_dir):
        self.src_dir = Path(src_dir).resolve()
        if re.match(r'(\d{8})$', self.src_dir.name): #source is temp directory, auto setup target out directory
            self.home_dir = Path(self.src_dir.anchor, datetime.now().strftime('%Y')+'@' + '{}'.format(os.environ.get('USERNAME')))
        else:
            self.home_dir = setupHomeDirectory(self.src_dir)

        if not self.home_dir:
            self.home_dir = Path(self.src_dir.anchor, datetime.now().strftime('%Y%m%d')) #target is temp directory either

        print('S/Target out collection directory is', self.home_dir)
        self.new_dir = self.home_dir

        self.succ_cnt, self.fail_cnt = 0, 0
        self.fail_not_match_cnt, self.succ_force_assigned_cnt = 0, 0
        self.duplicated_cnt, self.fail_conflict_cnt = 0, 0
        self.FAILURE_FILES = []
        self.min_dt, self.max_dt = datetime.max, datetime.min
        return

    def build_one(self, f):
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
                self.duplicated_cnt += 1
                f.unlink() #unlink old file
            else:
                self.fail_conflict_cnt += 1
                self.fail_cnt += 1
                self.FAILURE_FILES.append((f.resolve(), img_dt, name_dt, (dir_dt, dir_comments, is_assigned)))
                pass
            return
        
    def build(self):
        print('\n')
        #return
        for f in self.src_dir.glob('**/*.jpg'):
            print('\r', end='')    #Carriage return
            print('Processing', f.relative_to(self.src_dir), '...', end='')
            self.build_one(f)
            print('S({0}) F({1}) '.format(self.succ_cnt, self.fail_cnt), end='')
            if self.succ_cnt or self.fail_cnt or self.duplicated_cnt:
                print(': A({0}) N({1}) D({2}) C({3})'.format(
                    self.succ_force_assigned_cnt, self.fail_not_match_cnt, self.duplicated_cnt, self.fail_conflict_cnt), end='')
            print('-->', self.new_dir, end='...\t')

        '''Summary the results and remove some unused directories'''    
        print('\n')
        if self.max_dt != datetime.min:
            print('I/Image Datetime range {} .. {}\n'.format(self.min_dt, self.max_dt))
        if self.FAILURE_FILES:
            print('E/Total ({}) Failure Files:'.format(len(self.FAILURE_FILES)))
            for f in self.FAILURE_FILES:
                print('\t', f)

        if 1 or self.succ_cnt:
            res = removeEmptyDirectories(self.src_dir)
            if res == 0: #Remove source main directory. The directory must be empty.
                print('W/Removing source main directory', self.src_dir)
                self.src_dir.rmdir()
        return self

    def deepclean_one(self, last_dir_dt, last_subdir):
        if last_subdir and len(last_subdir) > 1:
            #print('W/deepclean on', last_dir_dt, last_subdir)
            all_items, dup_items = [], []

            for s in last_subdir: all_items.extend(sorted(s.iterdir(), key=lambda x: x.stem))
            #print('all_items', len(all_items), all_items)
            for i, f, in enumerate(all_items[:-1]):
                if f in dup_items: continue
                dup = list(filter(lambda n: filecmp.cmp(f, n), all_items[i+1:]))
                if dup:
                    print('W/Removing dup', f, dup)
                    for n in dup:
                        hash1 = hashlib.md5(f.open('rb').read())
                        hash2 = hashlib.md5(n.open('rb').read())
                        if f != n and hash1.hexdigest() == hash2.hexdigest(): #filecmp.cmp(f, n):  #double confirm for unlink dup items
                            dup_items.append(n)
                        else:
                            print('\tNOT SAME AS', f, n)
                            pass

            #remove all duplicate files
            for file in dup_items:
                print('E/Removing dup file', file)
                file.unlink()

            return

    def deepclean(self):
        if not self.src_dir.name.isdigit() or int(self.src_dir.name) not in VALID_YEARS:
            #print(self.src_dir.name)
            return

        print('I/Deepcleanning out collection directory', self.home_dir, '@', (self.min_dt.year, self.max_dt.year))
        for year in self.home_dir.iterdir():
            if not year.name.isdigit() or int(year.name) not in range(self.min_dt.year, self.max_dt.year+1): continue
            print(year)
            last_dir_dt = None
            last_subdir = []
            for subdir in sorted(year.iterdir(), reverse=True):
                print('\r', end='')    #Carriage return
                dir_dt, _, _ = getDatetimeFromDName(subdir)
                if dir_dt == last_dir_dt:
                    print('\t', subdir.name, end='...\t')
                    last_subdir.append(subdir)
                    pass
                else:
                    self.deepclean_one(last_dir_dt, last_subdir)
                    print('\t', subdir.name, end='...\t')
                    last_dir_dt = dir_dt
                    last_subdir = [subdir]

            self.deepclean_one(last_dir_dt, last_subdir)
            print('\n')
            #break

        return self

if __name__ == '__main__':
    print(sys.argv)
    #print(removeEmptyDirectories(r'D:\temp'))
    #setupHomeDirectory(Path(sys.argv[1]))
    if len(sys.argv) > 1:
        src_dir = Path(sys.argv[1])
        if (src_dir.is_dir()):
            Groups(src_dir).build().deepclean()
        else:
            print('E/Not found directory', src_dir)
    pass
