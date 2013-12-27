import sys, pprint
from findFeed import findFeed
from feedRead import parseFeed
from urlparse import urljoin

if __name__ == "__main__":
	feed = findFeed(sys.argv[1])	
	if len(feed) > 0:
		feedLink = urljoin(sys.argv[1], feed[0])
		pprint.pprint(parseFeed(feedLink))
	else:
		notfound = {'error': 'feed not found :(', 'url': sys.argv[1]}
		pprint.pprint(notfound)