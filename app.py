#! /usr/bin/python

from flask import Flask, render_template, request, url_for, redirect
import soundcloud

app = Flask(__name__)


def parseData(link):
	""" 
	parseData takes in a user's input url and returns the start interval of its
		most popular part, or -1 if the input is not valid
	parseData: string -> int """

	# create a client object with my app credentials
	client = soundcloud.Client(client_id='5c7a6aef6b14eab246a7e75b1b8840b6')

	# tracks = client.get('/tracks', q='felix jaehn')
	#link = "https://soundcloud.com/owslaofficial/what-so-not-high-you-are-1?in=samueljervis/sets/melodic-house"
	#link = 'https://soundcloud.com/kygo/m83-wait-kygo-remix'
	#track = client.get('/tracks/125621283')

	try:
		track = client.get('/resolve', url=link) 
		track_id = track.id
		is_streamable = track.streamable
		length = track.duration / 1000

		# if song is < 30 seconds, no need to find comments
		if length <= 30:
			return 0

		print track_id # for debug purposes
		print is_streamable


		comments = client.get('/tracks/%d/comments' % track_id, linked_partitioning = 1)
		numIntervals = length / 10
		hashmap = {}
		# initialize all intervals excluding 1st 10 seconds
		for x in xrange(1,numIntervals):
			hashmap[x] = 0
		hashmap = getvals(comments, hashmap)
		page = 1
		try:
			url = comments.next_href
			while url is not None and page < 9:
				print page
				page += 1
				comments = client.get(comments.next_href, linked_partitioning = page)
				hashmap = getvals(comments, hashmap)
				url = comments.next_href
		except AttributeError:
			print "Done"
		return findStartInterval(hashmap)
	except Exception:
		print 'Uh oh! This track cannot be found.'
	return -1


def getvals(aloc, hashmap):
	"""
	getvals - takes in a collection of comments and a dict and returns a map of the
		intervals of the song
	collection + dict(int:int) -> dict(int:int) """
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
	findStartInterval - finds the interval beginning the most popular part of the
		track
	dict(int:int) -> int """
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


@app.route('/')
def home():
	return render_template('index.html')


@app.route('/play', methods=['POST'])
def play():
	""" play gets the user input and parses it accordingly """
	link = request.form['inputBox']
	print "received"
	print link
	startTime = parseData(link)
	context = {}
	if (startTime == -1):
		context['code'] = -1
	else:
		context['code'] = 0
		endTime = (int(startTime) + 3) * 10
		startTime *= 10
		context['start'] = startTime
		context['end'] = endTime
		context['url'] = "https://w.soundcloud.com/player/?url=" + link + "&color=83d2ce"+"&autoplay=false"
	return render_template('play.html', **context)



if __name__ == '__main__':
	app.run(debug=True)
	
	






