import feedparser
import os
import re
import sys
from sh import mkdir

_SPACES = re.compile(r'[ ]+')
_INVALID_PATH_CHARS = re.compile(r'[^a-zA-Z0-9_\-]')

def usage():
  print 'usage: ' + sys.argv[0] + ' [url of blog]'
  exit()

def get_rss(url):
  url = url.rstrip('/') + '/rss'
  if not url.startswith('http'):
    url = 'http://' + url
  return feedparser.parse(url)

def sanitize_path(s):
  s = re.sub(_INVALID_PATH_CHARS, ' ', s)
  s = re.sub(_SPACES, '_', s)
  s = s.lower().strip('_')
  return s

def write_entry(dir, entry):
  with open(dir + '/index.html', 'w') as f:
    f.write(entry.description.encode('utf-8'))

def mkdirs(d):
  print 'Output for feed: ' + d.feed.title
  out_dir = sanitize_path(d.feed.title)
  if os.path.exists(out_dir):
    print 'cannot continue, directory ' + out_dir + ' already exists'
    return False
  mkdir(out_dir)
  for entry in d.entries:
    entry_dir = out_dir + '/' + sanitize_path(entry.title)
    print entry_dir
    mkdir(entry_dir)
    write_entry(entry_dir, entry)

if __name__ == '__main__':
  if len(sys.argv) != 2:
    usage()

  url = sys.argv[1]
  feed = get_rss(url)
  mkdirs(feed)
