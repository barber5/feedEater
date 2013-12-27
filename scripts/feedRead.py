import sys, mechanize, feedparser, traceback, operator, pprint
from bs4 import BeautifulSoup, NavigableString
from bs4.element import Comment
from util import getHtmlFromUrl, stringifySoup
from nltk.tokenize import sent_tokenize, word_tokenize


def parseFeed(feedUrl):
	d = feedparser.parse(feedUrl)
	return d

def getNavStrs(soup):
	result = []
	try:
		if not hasattr(soup, 'contents'):
			print >> sys.stderr, 'big fuckup, here is my soup'+unicode(soup)

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
		sys.exit(0)


def getKmersForStr(s, k):
	result = []
	for i in range(len(s) - k + 1):
		result.append(s[i:i+k])
	return result

def mapKmersForNavStrs(navStrs, k):
	result = {}
	for i,ns in enumerate(navStrs):
		kmers = getKmersForStr(unicode(ns), k)
		for kmer in kmers:
			if kmer not in result:
				result[kmer] = []
			result[kmer].append(i)
	return result


def getTagPath(node, path):
	if(isinstance(node, NavigableString)):
		path = 'navStr' 

	else:
		name = node.name
		
		if 'class' in node.attrs:
			name += '-'+unicode(node.attrs['class'])
		path = name + ' '+ path
	if node.parent:
			path = str(node.parent.contents.index(node)) + path

	if node.parent:
		return getTagPath(node.parent, path)
	else:
		return path

def getSentenceTagPathMap(soup):
	result = {}
	nStrs = getNavStrs(soup)
	for ns in nStrs:
		for sent in sent_tokenize(unicode(ns)):
			sentStr = sent		
			if sentStr not in result:
				result[sentStr] = []
			result[sentStr].append(getTagPath(ns, ''))
	return result

def getWordTagPathMap(soup):
	result = {}
	nStrs = getNavStrs(soup)
	for ns in nStrs:
		for sent in sent_tokenize(unicode(ns)):
			toks = word_tokenize(sent)
			for i in range(len(toks) - 1):
				word = (toks[i], toks[i+1])
				if word not in result:
					result[word] = []
				result[word].append(getTagPath(ns, ''))
	return result

def getSentences(soup):
	nStrs = getNavStrs(soup)
	result = []
	for ns in nStrs:
		for sent in sent_tokenize(unicode(ns)):
			sentStr = sent
			result.append(sentStr)
	return result

def getBySent(entry, content):
	cSoup = BeautifulSoup(content)
	html = getHtmlFromUrl(entry['link'])
	pSoup = BeautifulSoup(html)

	cSents = getSentences(cSoup)
	pSentMap = getSentenceTagPathMap(pSoup.body)
	paths = {}
	for sent in cSents:
		if sent in pSentMap:
			for path in pSentMap[sent]:
				if path not in paths:
					paths[path] = 0
				paths[path] += len(word_tokenize(sent))
	for k,v in paths.iteritems():
		if v > 0:
			print k,'\t',v
	return paths

def getWords(content):  # actually this will get bigrams, watch out
	result = []
	wsoup = BeautifulSoup(content)
	content = stringifySoup(wsoup)
	for sent in sent_tokenize(content):
		toks = word_tokenize(sent)
		for i in range(len(toks) - 1):
			result.append((toks[i], toks[i+1]))
	return result

def getByWord(entry, content):	
	html = getHtmlFromUrl(entry['link'])
	pSoup = BeautifulSoup(html)
	cWords = getWords(content)	
	pWordMap = getWordTagPathMap(pSoup.body)
	pprint.pprint(pSoup.body)	
	paths = {}
	for word in cWords:
		if word in pWordMap:
			for path in pWordMap[word]:
				if path not in paths:
					paths[path] = 0
				paths[path] += 1
	for k,v in paths.iteritems():
		if v > 0:
			print k,'\t',v
	return paths

def getLCAForPaths(p1, p2):
	for i in range(min(len(p1), len(p2))):
		if p1[i] != p2[i]:
			return i
	return min(len(p1), len(p2))


# scoring this path could be better than just counting
# we could have an increased score for not ending on html or body or being in
# head
# could also increase the score for ending on div or article
def getPrefixPath(p1, p2):
	prefix = ''
	for i in range(min(len(p1), len(p2))):
		if p1[i] != p2[i]:
			return prefix
		else:
			if len(prefix) > 0:
				sp = ' '
			else:
				sp = ''
			prefix += sp + p1[i]
	return prefix

def pickBestPath(paths):
	total = 0
	lcaPairs = {}
	prefixes = {}
	for p1 in paths.keys():
		for p2 in paths.keys():
			if p1 == p2:
				continue
			if (p2, p1) in lcaPairs:
				continue
			lca = getLCAForPaths(p1.split(' '), p2.split(' '))
			prefixPath = getPrefixPath(p1.split(' '), p2.split(' '))
			if prefixPath not in prefixes:
				prefixes[prefixPath] = 0
			prefixes[prefixPath] += paths[p1]
			lcaPairs[(p1, p2)] = lca
	
	return max(prefixes.iteritems(), key=operator.itemgetter(1))[0]
	



def getWrapper(feedEntity):
		#todo if there's one article tag in the whole thing, return that right away, that's the wrapper
		if len(feedEntity.entries) == 0:
			print 'no feedEntity entries'
			pprint.pprint(feedEntity)
			return
		entry = feedEntity.entries[0]
		
		paths = {}
		if hasattr(entry, 'content'):
			content = entry.content[0]['value']
			paths = getBySent(entry, content)
		elif hasattr(entry, 'summary_detail'):
			content = entry.summary_detail['value']
			paths = getByWord(entry, content)
		elif hasattr(entry, 'summary'):
			content = entry.summary
			paths = getByWord(entry, content)
		else:
			print >> sys.stderr, "Ooops, can't find content in feed: "+unicode(feedEntity)
			return

		return pickBestPath(paths)

if __name__ == "__main__":
	print >> sys.stderr, parseFeed(sys.argv[1])