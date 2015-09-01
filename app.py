#! /usr/bin/python

from flask import Flask, render_template, request, url_for, redirect, make_response
import soundcloud
import requests

app = Flask(__name__)

# create a client object with my app credentials
client = soundcloud.Client(client_id='5c7a6aef6b14eab246a7e75b1b8840b6')

def getTrackComments(track_id, length):
  """
  getTrackComments takes in a track id and its length and outputs the start 
    interval of the most popular part
  getTrackComments: int, int -> int """

  # if song is < 30 seconds, no need to find comments
  if length <= 30:
    return 0

  print track_id # for debug purposes

  page = 1
  print page
  comments = client.get('/tracks/%d/comments' % track_id, linked_partitioning = page)
  numIntervals = length / 10
  hashmap = {}
  # initialize all intervals in hashmap excluding 1st 10 seconds
  for x in xrange(1,numIntervals):
    hashmap[x] = 0
  hashmap = getvals(comments, hashmap)
  
  try:
    url = comments.next_href
    while url is not None and page < 3: # load no more than 600 coments to analyze
      page += 1
      print page
      comments = client.get(comments.next_href, linked_partitioning = page)
      hashmap = getvals(comments, hashmap)
      url = comments.next_href
  except AttributeError:
    print "Done"
  return findStartInterval(hashmap)


def parseData(link):
  """ 
  parseData takes in a user's input and returns a tuple of its type 
    (playlist, user, or track) and the start interval of its most popular
    part, or -1 if the input is not valid
  parseData: string -> dict(int, int) """

  # tracks = client.get('/tracks', q='felix jaehn')
  #link = "https://soundcloud.com/owslaofficial/what-so-not-high-you-are-1?in=samueljervis/sets/melodic-house"
  #track = client.get('/tracks/125621283')
  data = {}
  data['inputType'] = 0
  data['startTime'] = -1
  try:
    userInput = client.get('/resolve', url=link)
    if userInput.kind == 'playlist': 
      print userInput.track_count

      track_id = userInput.tracks[0][u'id']
      length = userInput.tracks[0][u'duration']
      data['inputType'] = 1
      data['startTime'] = getTrackComments(track_id, length)
    elif userInput.kind == 'user':
      pass
    elif userInput.kind == 'track':
      data['startTime'] = getTrackComments(userInput.id, userInput.duration)
  except requests.exceptions.HTTPError:
    print 'Uh oh! This track cannot be found.'
    try:
      search = client.get('/tracks', q=link)
      for track in search:
        print track.title
    except Exception, e:
      print link + " cannot be found"
  return data


def getvals(aloc, hashmap):
  """
  getvals - takes in a collection of comments and a dict and returns a map of the
    intervals of the song
  getvals: collection + dict(int:int) -> dict(int:int) """
  for comment in aloc.collection:
    time = comment[u'timestamp'] # timestamp of comment in milliseconds
    if isinstance(time, int): # makes sure there is a timestamp
      time /= 1000
      key = time / 10 
      if time > 0 and key in hashmap:
        hashmap[key] += 1
  return hashmap


def findStartInterval(hashmap):
  """
  findStartInterval - finds the interval beginning the most popular 30s of the
    track
  findStartInterval: dict(int:int) -> int """
  # Find interval with most comments, excluding the first 20 seconds due to noise
  peakInterval = (0, 0) 
  for key in hashmap.keys():
    value = hashmap[key]
    if (key > 1 and peakInterval[1] <= value):
      peakInterval = (key, value)

  # Search for the top intervals around the peak, to find best sequence
  key = peakInterval[0]
  if (key == 2): # first 2 intervals excluded due to noise in data
    return key
  else:
    num1 = hashmap[key - 2] # check 2 intervals both sides of peak
    num2 = hashmap[key - 1]
    num4 = hashmap[key + 1]
    num5 = hashmap[key + 2]
    sum1 = num1 + num2
    sum2 = num2 + num4
    sum3 = num4 + num5
    start = max(sum1, sum2, sum3)
    if (start == sum1):
      key -= 2
    elif (start == sum2):
      key -= 1
  return key


def convertTime(timeInSeconds):
  """
  convertTime converts time in seconds to a string in mm:ss 
  convertTime: int -> str """
  minutes = str(timeInSeconds / 60)
  seconds = timeInSeconds % 60
  if (seconds < 10):
    s = "0" + str(seconds)
    return minutes + ":" + s
  return minutes + ":" + str(seconds)


@app.route('/')
def home():
  """ home page """
  return render_template('index.html')


@app.route('/play', methods=['POST'])
def play():
  """ 
  play gets the user input, parses it accordingly, and renders the new 
    play page 
  play: -> new page """

  link = request.form['inputBox']
  data = parseData(link)
  dataType = data['inputType']
  startTime = data['startTime']
  context = {}
  if (startTime == -1):
    context['code'] = -1
  else:
    context['code'] = 0
    endTime = (startTime + 3) * 10
    startTime *= 10
    context['beginTime'] = convertTime(startTime)
    context['endTime'] = convertTime(endTime)
    context['start'] = startTime
    context['end'] = endTime
    context['url'] = ("https://w.soundcloud.com/player/?url=" + link
      + "&color=83d2ce"+"&autoplay=false")
  return render_template('play.html', **context)



if __name__ == '__main__':
  app.run(debug=True)
  
  






