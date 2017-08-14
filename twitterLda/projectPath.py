import os

curdir = os.path.dirname(os.path.abspath(__file__))
rootdir = os.path.normpath(os.path.join(curdir, os.path.pardir))
datadir = os.path.join(rootdir, 'data')

if __name__ == '__main__':
  print curdir
  print rootdir
  print datadir