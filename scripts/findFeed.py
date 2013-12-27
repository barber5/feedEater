import sys, mechanize, re, feedparser
from bs4 import BeautifulSoup
from util import getHtmlFromUrl

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

if __name__ == "__main__":
	print findFeed(sys.argv[1])