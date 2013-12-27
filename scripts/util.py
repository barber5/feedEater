import mechanize, sys, traceback, urllib, urllib2, json
from bs4 import NavigableString, Comment

user_agent = 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.22 (KHTML, like Gecko) Chrome/25.0.1364.172 Safari/537.22'
srv = '54.193.75.112'

def getHtmlFromUrl(link):
	br = mechanize.Browser()
	br.addheaders = [('user-agent', user_agent)]
	r = br.open(link)

	html = r.read()

	return html

def getNavStrs(soup, die=True):
	result = []
	try:
		if not hasattr(soup, 'contents'):
			None
			#print >> sys.stderr, 'oops, here is my soup'+unicode(soup)

		for child in soup.contents:
			if(isinstance(child, NavigableString)) and not isinstance(child, Comment):
				result.append(child)
			elif isinstance(child, Comment):
				None
			else:
				result.extend(getNavStrs(child))             
		return result

	except Exception as e:
		print >> sys.stderr, unicode(e)
		print >> sys.stderr, soup
		tb = traceback.format_exc()
		print >> sys.stderr, unicode(tb)
		if(die):
			sys.exit(0)

def stringifySoup(soup):
	return ' '.join(getNavStrs(soup)).strip()