import feedparser
import lxml.html as html
import os
import re
import requests
import subprocess
import sys
import time
from sh import mkdir

_API_BASE = 'http://api.tumblr.com/v2/blog'
_INVALID_PATH_CHARS = re.compile(r'[^a-zA-Z0-9_\-]')
_SPACES = re.compile(r'[ ]+')

with open(os.path.dirname(__file__) + 'api_key') as f:
  _API_KEY = f.read().strip()

url = None

def usage():
  print 'usage: ' + sys.argv[0] + ' [url of blog]'
  exit()

def req(path, **kwargs):
  target = '%s/%s/%s?api_key=%s' % (_API_BASE, url, path, _API_KEY)
  for arg in kwargs:
    target += '&%s=%s' % (arg, kwargs[arg])
  print 'requesting ', target
  req = requests.get(target)
  res = req.json()['response']
  return res

def sanitize_path(s):
  s = re.sub(_INVALID_PATH_CHARS, ' ', s)
  s = re.sub(_SPACES, '_', s)
  s = s.lower().strip('_')
  return s

def write_images(dir, post):
  photos = post['photos']
  for i, photo in enumerate(photos):
    src = photo['original_size']['url']
    print 'download post photo %d/%d' % (i + 1, len(photos))
    subprocess.check_call('curl %s > %s/i%02d.png' % (src, dir, i), shell=True)

def write_entry(out_dir, post):
  print 'saving ' + post['slug']
  dir = out_dir + '/' + post['slug']
  mkdir(dir)

  type = post['type']
  if type == 'photo':
    content = post['caption']
    write_images(dir, post)
  elif type == 'text':
    content = post['body']
  else:
    print 'don\'t know how to handle type ' + type
    return

  with open(dir + '/index.html', 'w') as f:
    f.write(content.encode('utf-8'))

def mkdirs(name, num):
  print 'Output for feed %s (%d posts)' % (name, num)
  out_dir = sanitize_path(name)
  if os.path.exists(out_dir):
    print 'cannot continue, directory ' + out_dir + ' already exists'
    return False
  mkdir(out_dir)
  for i in range(0, num, 20):
    posts = req('posts', offset=i)['posts']
    for post in posts:
      write_entry(out_dir, post)
  return
  for entry in d.entries:
    entry_dir = out_dir + '/' + sanitize_path(entry.title)
    print entry_dir
    mkdir(entry_dir)
    write_entry(entry_dir, entry)

if __name__ == '__main__':
  if len(sys.argv) != 2:
    usage()

  url = sys.argv[1]
  info = req('info')['blog']
  name = info['title']
  num = info['posts']
  mkdirs(name, num)
