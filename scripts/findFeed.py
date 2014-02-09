import sys, mechanize, re, feedparser
from bs4 import BeautifulSoup
from util import getHtmlFromUrl, postData
from config import domain

domain = 'localhost'

feed_endpoint = 'http://{}:3000/feed'.format(domain)

def findFeedFromHtml(html):
	soup = BeautifulSoup(html)
	links = soup.find_all("link", type=re.compile("rss"))	
	urls = soup.find_all("a", href=re.compile('.+'))
	
	for url in urls:
		if re.search(r'rss', unicode(url)):
			print >> sys.stderr, 'Trying '+url['href']
			d = feedparser.parse(url['href'])
			if len(d.entries) > 0:				
				links.append(url)
	return links

def findFeed(url):
	html = getHtmlFromUrl(url)	
	links = findFeedFromHtml(html)
	result = []
	for link in links:
		result.append(link.attrs['href'])

	return result

def findAndStore(url, name):
	feeds = findFeed(url)
	for feed in feeds:
		pd = {
			'name': name,
			'feed_url': feed,
			'blog_url': url
		}
		print postData(feed_endpoint, pd)

if __name__ == "__main__":
	# usage link and name
	findAndStore(sys.argv[1], sys.argv[2])