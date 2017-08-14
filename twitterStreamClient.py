'''
twitterStreamClient.py

A client for Twitter Streaming API. Listen to a filtered tweet stream 
and save JSON of each tweet to an output file, one line for each entry.
Provided class and function can be imported to other code.
The main function has default parameters configured and will save text file
to data/tweets with file name being current date and time.

Oras Phongpanangam
'''

from __future__ import print_function

import tweepy
import json
import time
from datetime import *
import sys
from codecs import open
import os

# edit these parameters as needed

query = ['foursquare', '4sq', 'swarmapp']
outputFileDir = 'data/tweets'

###############################################################################

# read authentication information from 'twitterAuth.json' file
try:
  with open('twitterAuth.json', 'r') as authFile:
    authDict = json.loads(authFile.read())
    consumerKey    = authDict['consumerKey']
    consumerSecret = authDict['consumerSecret']
    token          = authDict['token']
    tokenSecret    = authDict['tokenSecret']
except IOError:
  print('Authentication file not found ("twitterAuth.txt" in root dir)')
  sys.exit()

auth = tweepy.OAuthHandler(consumerKey, consumerSecret)
auth.set_access_token(token, tokenSecret)

class MyStreamListener(tweepy.StreamListener):
  '''
  Stream listener to use with Tweepy streaming api and write JSON output and logs to file

  :param outFile: file to write JSON output with each line as one tweet
  :param logFile: file to write logs
  '''
  def __init__(self, outFile, logFile):
    self.out = outFile
    self.log = logFile
    super(MyStreamListener, self).__init__()

  def printLog(self, string):
    logString = '[{}] '.format(datetime.now())+string
    print(logString)
    print(logString, file=self.log)

  def printOut(self, string):
    print(string, file=self.out)

  def on_connect(self):
    self.printLog('Connection established')

  def on_status(self, status):
    '''
    self.printOut(','.join([datetime.now().isoformat(), 
                    status.id_str, 
                    status.text, 
                    status.user.id_str, 
                    status.user.screen_name, 
                    json.dumps(status._json)]))
    '''
    self.printOut(json.dumps(status._json))
    try:
      self.printLog('Tweet received; {} : {}'.format(status.user.screen_name, status.text.encode('utf-8', 'ignore')))
    except:
      self.printLog('Tweet received; cannot encode')

  def on_limit(self, track):
    self.printLog('Limit warning; track={}'.format(track))

  def on_error(self, status_code):
    self.printLog('Error; status_code={}'.format(status_code))
    
  def on_timeout(self):
    self.printLog('Timeout')

  def on_disconnect(self, notice):
    self.printLog('Disconnect; notice={}'.format(notice))
    self.out.close()
    self.log.close()

  def on_warning(self, notice):
    self.printLog('Warning; notice={}'.format(notice))


def startStream(streamListener, query, languages=['en']):
  '''
  Start listening to Twitter Streaming API filtered with supplied query and language

  :param streamListenter: stream listener object to use
  :param query:           query to use as filter
  :param language:        list of languages 2 characters symbol
  '''
  myStream = tweepy.Stream(auth=auth, listener=myStreamListener)
  myStream.filter(track=query, languages=languages, async=False)


if __name__ == '__main__':
  
  outFileName = os.path.join(outputFileDir, 'twitter_{}.txt'.format(datetime.now().strftime('%Y_%m_%d_%H%M%S')))
  logFileName = os.path.join(outputFileDir, 'twitter_{}.log'.format(datetime.now().strftime('%Y_%m_%d_%H%M%S')))
  outFile = open(outFileName, 'w', encoding='utf-8')
  logFile = open(logFileName, 'w', encoding='utf-8')

  myStreamListener = MyStreamListener(outFile, logFile)
  startStream(myStreamListener, query, ['en']) 