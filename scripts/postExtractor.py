import sys, mechanize, re, urlparse, pprint, time
from bs4 import BeautifulSoup
from random import random
from util import getHtmlFromUrl, postData, stringifySoup

def extractPost(url, post_rule):
	result = {
		'title': '',
		'byline': '',
		'post_date': '',
		'comments': [],
		'content': ''
	}
	html = getHtmlFromUrl(url)
	soup = BeautifulSoup(html)
	s_title = soup.select(post_rule['title'])
	if s_title and len(s_title) > 0:
		result['title'] = stringifySoup(s_title[0])
	s_byline = soup.select(post_rule['byline'])
	if s_byline and len(s_byline) > 0:
		result['byline'] = stringifySoup(s_byline[0])
	s_postdate = soup.select(post_rule['post_date'])
	if s_postdate and len(s_postdate) > 0:
		result['post_date'] = stringifySoup(s_postdate[0])
	s_content = soup.select(post_rule['content'])
	if s_content and len(s_content) > 0:
		result['content'] = stringifySoup(s_content[0])
	#todo add comments
	print result
	return result

def extractPosts(post_rule, url):
	result = []
	html = getHtmlFromUrl(url)
	soup = BeautifulSoup(html)
	postListRule = post_rule['postlist']
	postUrls = soup.select(postListRule)
	return [urlparse.urljoin(url, pu.attrs['href']) for pu in postUrls]
	'''
	if postUrls:
		for pu in postUrls:
			href = pu.attrs['href']
			result.append(extractPost(urlparse.urljoin(url, href), post_rule))
			print 'sleeping'
			time.sleep(10+20*random())
			print 'awake'
	if len(result) > 0:
		page_s = soup.select(page_rule)
		if page_s:
			nextPage = urlparse.urljoin(url, page_s.attrs['href'])
			nextPosts = extractPosts(post_rule, page_rule, nextPage)
			result.extend(nextPosts)
	return result
	'''
def getNextPage(page_rule, url):
	html = getHtmlFromUrl(url)
	soup = BeautifulSoup(html)
	url_s = soup.select(page_rule)
	if url_s:
		try:
			return url_s[0].attrs['href']
		except Exception as e:
			return None


if __name__ == "__main__":
	post_rule = {
		'title':  'h1.entry-title',
		'byline': 'span.author > span.fn',
		'post_date': 'p.headline_meta > abbr.published',
		'content': 'div.post > div.entry-content',
		'postlist': 'h2.entry-title > a'
	}
	page_rule = 'p.previous > a'
	posts = extractPosts(post_rule, sys.argv[1])
	np = urlparse.urljoin(sys.argv[1], getNextPage(page_rule, sys.argv[1]))
	posts.extend(extractPosts(post_rule, np))
	np = urlparse.urljoin(np, getNextPage(page_rule, np))
	posts.extend(extractPosts(post_rule, np))
	print posts

	