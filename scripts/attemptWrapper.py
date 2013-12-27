import sys, pprint
from findFeed import findFeed
from feedRead import parseFeed, getWrapper
from urlparse import urljoin


if __name__ == "__main__":
	feed = findFeed(sys.argv[1])	
	if len(feed) > 0:
		feedLink = urljoin(sys.argv[1], feed[0])
		entries = parseFeed(feedLink)
		print getWrapper(entries)
	else:
		print 'no feed found :('