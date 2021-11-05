#!/usr/bin/python3
# -*- coding: utf-8 -*-

import setuptools
import os
import sys

sys.path.append(os.path.join(os.getcwd()))
version_file = os.path.join(os.path.join(os.getcwd(), '.VERSION'))


def _split_version_nb(l):
    return int(l.split('=')[1].replace(' ', ''))


def _exists_version_file(path):
    p = os.path.join(path)
    if os.path.exists(p):
        return True
    else:
        raise FileNotFoundError(path + " doesn't exist")

    
def _read_version_file():
    if _exists_version_file(version_file):
        f_r = open(version_file, 'r')
        major = ''
        minor = ''
        build = ''
        for l in f_r.readlines():
            if 'MAJOR = ' in l:
                major = _split_version_nb(l)
            elif 'MINOR = ' in l:
                minor = _split_version_nb(l)
            elif 'BUILD =' in l:
                build = _split_version_nb(l)
        f_r.close()
#        print (major, minor, build)
        if isinstance(major, int) and \
           isinstance(minor, int) and \
           isinstance(build, int):
            return major, minor, build
        else:
            raise ValueError('_read_version_file(): '
                             + 'no VERSION file, or no major/minor/... present')

        
def get_version():
    major, minor, build = _read_version_file()
    return '%s.%s.%s' % (str(major), str(minor), str(build))

    
def set_build():
    if _exists_version_file(version_file):
        (major, minor, build) = _read_version_file()
        print('Old version: ' + str(major) + \
              '.' + str(minor) + '.' + str(build))
        f_w = open(version_file, 'w')
        f_w.write('MAJOR = ' + str(major) + '\n')
        f_w.write('MINOR = ' + str(minor) + '\n')
        f_w.write('BUILD = ' + str(build + 1) + '\n')
        f_w.close()
        (major, minor, build) = _read_version_file()
        version_string = 'New version: ' + str(major) + \
                         '.' + str(minor) + '.' + str(build)
        print('%s' % version_string)
        return version_string

    
def list_py_modules(): 
    py_files = []
    for f in os.listdir(os.getcwd()):
        basename, ext = os.path.splitext(f)
        if ext == '.py':
            if basename != 'setup':
                py_files.append(basename)
    return py_files 


if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == '--set-build':
        set_build()
    else:
        setuptools.setup (
            name = 'pl0t', 
            version = get_version(),
            author = 'Benoit FREMON', 
            author_email = 'ben@in.volution.fr',
            description = 'Wrapper & convenience funcs for seaborn',
            long_description_content_type = 'text/markdown',
            url = 'https://dev.volution.fr',
            packages = setuptools.find_packages(),
            classifiers=[
                "Programming Language :: Python :: 3",
                "License :: OSI Approved :: MIT License",
                "Operating System :: OS Independent",
            ],
            python_requires='>=3.6'
        )

        
        
