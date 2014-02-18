import mechanize, sys, traceback, urllib, urllib2, json, random
from bs4 import NavigableString, Comment, BeautifulSoup
import gearman, redis, os, sys, psycopg2, traceback, smtplib
from access import AssetManager, AccessManager, AssetException
import smtplib, json, datetime, time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config import default_page_size
import urlparse
from db import new_object, update_object

user_agent = 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.22 (KHTML, like Gecko) Chrome/25.0.1364.172 Safari/537.22'


def exceptionPrinter(e):    
    print >> sys.stderr, unicode(e)+'\ntraceback: '+unicode(traceback.format_exc())

class CursorWrap:
    def __init__(self, cfg):
        try:
            self.conn = psycopg2.connect(database=cfg['database'], user=cfg['user'], host=cfg['host'], port=cfg['port'], password=cfg['password'])
            self.cur = self.conn.cursor()
        except Exception as e:
            exceptionPrinter(e)
            raise AssetException('could not get database connection')
    def execute(self, stmt, replacement):
        try:            
            self.cur.execute(stmt, replacement)
            self.conn.commit()
        except Exception as e:
            exceptionPrinter(e)
            raise AssetException('could not execute database query')
    def mogrify(self, stmt, replacement):
        try:            
            return self.cur.mogrify(stmt, replacement)            
        except Exception as e:
            exceptionPrinter(e)
            raise AssetException('could not execute database query')
        

    def fetchone(self):
        try:
            return self.cur.fetchone()
        except Exception as e:
            exceptionPrinter(e)        
            raise AssetException('could not execute database query')

    def fetchall(self):
        try:
            return self.cur.fetchall()
        except Exception as e:
            exceptionPrinter(e)            
            raise AssetException('could not execute database query')

    def cleanup(self):        
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()

    def fetchSpecial(self, cfg):
        None


class CrawlWrap():
    def __init__(self, crawlHash, domainHash, crawlDelay, randomDelay):
        self.crawlHash = crawlHash
        self.domainHash = domainHash
        self.crawlDelay = crawlDelay
        self.randomDelay = randomDelay

    def addCrawl(self, resourceId, resourceType, client, cur):
        cacheIt = {
            'resourceId': resourceId,
            'resourceType': resourceType
        }
        if resourceType == 'post':
            query = "SELECT post_url FROM posts where id=%s;"
        elif resourceType == 'feed':
            query = "SELECT blog_url FROM feeds where id=%s;"            
        else:
            raise AssetException("invalid resourceType in addCrawl")
        cur.execute(query, [resourceId])
        rows = cur.fetchall()
        nameMapping = {
            'resource': {
                0: 'url'
            }
        }
        dbResult = joinResult(rows, nameMapping)
        if dbResult['resource']['url']:
            cacheIt['url'] = dbResult['resource']['url']
            hn = urlparse.urlparse(dbResult['resource']['url']).hostname
            if hn:                
                client.sadd(self.crawlHash+":"+hn, json.dumps(cacheIt))
                domain = client.hget(self.domainHash, hn)
                if domain:
                    None
                else:
                    client.hset(self.domainHash, hn, 0)
            else:
                raise AssetException("Invalid url stored")
        else:
            raise AssetException("No url for resource")
    
    def doWork(self, client, cursor, resId=None, domain=None):
        domains = client.hgetall(self.domainHash)
        for name, value in domains.iteritems():
            if domain:
                if name != domain:
                    continue
            lastCrawl = int(value)
            millis = int(round(time.time()))
            if millis - lastCrawl > self.crawlDelay + self.randomDelay*random.random():   
                if resId:
                    members = client.smembers(self.crawlHash+":"+name)
                    for mem in members:
                        cacheIt = json.loads(mem)
                        if cacheIt['resourceId'] == resId and cacheIt['resourceType'] == 'post':
                            self.crawlPost(cursor, cacheIt)
                            client.srem(self.crawlHash+':'+name, mem)
                            return cacheIt
                        elif cacheIt['resourceId'] == resId and cacheIt['resourceType'] == 'feed':
                            self.crawlFeed(client, cursor, cacheIt)
                            client.srem(self.crawlHash+':'+name, mem)
                            return cacheIt
                else:
                    members = client.smembers(self.crawlHash+":"+name)
                    for mem in members:
                        cacheIt = json.loads(mem)
                        if cacheIt['resourceType'] == 'post':
                            self.crawlPost(cursor, cacheIt)
                            client.srem(self.crawlHash+':'+name, mem)
                            break
                        elif cacheIt['resourceType'] == 'feed':
                            self.crawlFeed(client, cursor, cacheIt)
                            client.srem(self.crawlHash+':'+name, mem)
                            break
                                                            
                    client.hset(self.domainHash, name, str(millis))
                    cacheIt['domain'] = name
                    return cacheIt
        return {'domain': "throttled, or no work to do"}

    def crawlPost(self, cur, cacheIt):
        query = "SELECT fe.extraction_rule, po.feed_id from posts po inner join feeds fe on fe.id=po.feed_id where po.id=%s"
        cur.execute(query, [cacheIt['resourceId']]) 
        print cur.mogrify(query, [cacheIt['resourceId']])   
        rows = cur.fetchall()        
        nameMapping = {
            'blog': {
                0: 'extraction_rule',
                1: 'feed_id'                
            }
        }
        dbResult = joinResult(rows, nameMapping)        
        post = extractPost(cacheIt['url'], json.loads(dbResult['blog']['extraction_rule']))
        post['post_id'] = cacheIt['resourceId']
        print post
        update_object(cur, 'posts', 'post_id', post)

    def crawlFeed(self, client, cur, cacheIt):        
        query = "SELECT extraction_rule, pagination_rule, blog_url, post_url FROM feeds left outer join posts on feeds.id=posts.feed_id where feeds.id=%s"  
        cur.execute(query, [cacheIt['resourceId']])   
        rows = cur.fetchall()
        nameMapping = {
            'blog': {
                0: 'extraction_rule',
                1: 'pagination_rule',
                2: 'blog_url',
                'posts': [{
                    3: 'post_url'
                }]
            }
        }
        dbResult = joinResult(rows, nameMapping)
        nextPosts = {}
        for po in dbResult['blog']['posts']:
            nextPosts[po['post_url']] = False
        dbResult['blog']['posts'] = nextPosts   
        if not dbResult['blog']['extraction_rule'] or not dbResult['blog']['pagination_rule']:
            return {"error": "extraction rules missing"}
        postUrls = extractPosts(json.loads(dbResult['blog']['extraction_rule']), dbResult['blog']['blog_url'])
        print postUrls
        newPosts = []
        postsToGrab = set([])
        for pu in postUrls:
            print pu
            if pu not in dbResult['blog']['posts']:         
                newPosts.append(pu)
            else:
                print dbResult['blog']['posts'][pu]
        print newPosts
        postsToGrab = postsToGrab | set(newPosts)
        lastPage = dbResult['blog']['blog_url']
        tries = 0
        tolerance = 2 # go two pages without seeing something new before giving up
        while len(newPosts) > 0 or tries < tolerance:
            if len(newPosts) == 0:
                print 'no new posts!'
                print 'tries: '+str(tries)
                tries += 1
            else:
                tries = 0            
            newPosts = []
            nextPage = getNextPage(dbResult['blog']['pagination_rule'], lastPage)        
            print 'nextPage'*100
            print nextPage    
            if not nextPage:
                break
            postUrls = extractPosts(json.loads(dbResult['blog']['extraction_rule']), nextPage)
            for pu in postUrls:
                if pu not in dbResult['blog']['posts'] and pu not in postsToGrab:
                    newPosts.append(pu)
            postsToGrab = postsToGrab | set(newPosts)   
            
            print postsToGrab
            for pu in postsToGrab:  
                postData = {
                    'feed_id': cacheIt['resourceId'],
                    'post_url': pu
                }
                print 'inserting {}'.format(pu)         
                new_object(cur, 'posts', postData)                      
                dbResult['blog']['posts'][pu] = True
            postsToGrab = set([])        
            print postsToGrab

            lastPage = nextPage
            print 'sleeping....'
            time.sleep(self.crawlDelay+self.randomDelay*random.random())
            print 'awake!'  
    def getWorkStats(self, client, cur):
        domains = client.hgetall(self.domainHash)    
        result = []    
        print domains
        for name, value in domains.iteritems():
            domainRes = {'posts': [], 'feeds': [], 'domain': name}
            lastCrawl = int(value)
            millis = int(round(time.time()))
            delt = millis - lastCrawl
            members = client.smembers(self.crawlHash+":"+name)
            for mem in members:
                cacheIt = json.loads(mem)
                if cacheIt['resourceType'] == 'post':
                     domainRes['posts'].append(cacheIt)                   
                elif cacheIt['resourceType'] == 'feed':
                    domainRes['feeds'].append(cacheIt)
            result.append(domainRes)
        return result
                



def redisPool(cfg):
    if 'host' not in cfg or 'port' not in cfg:
        raise AssetException()
    pool = redis.ConnectionPool(host=cfg['host'], port=cfg['port'])
    return pool

def dbCursor(cfg):
    if 'database' not in cfg or 'user' not in cfg or 'host' not in cfg or 'port' not in cfg:
        raise AssetException()
    result = CursorWrap(cfg)
    return result

def s3Bucket(cfg):
    if 'access' not in cfg or 'secret' not in cfg or 'bucketName' not in cfg:
        raise AssetException()
    conn = S3Connection(access, secret)
    bucket = conn.get_bucket(bucketName)
    return bucket

def crawlHandler(cfg):
    if 'crawlHash' not in cfg or 'domainHash' not in cfg or 'crawlDelay' not in cfg or 'randomDelay' not in cfg:
        raise AssetException()
    cw = CrawlWrap(cfg['crawlHash'], cfg['domainHash'], cfg['crawlDelay'], cfg['randomDelay'])
    return cw


assetManager = AssetManager()
assetManager.registerAssetFunction(redisPool, "redisPool")
assetManager.registerAssetFunction(dbCursor, "dbCursor")
assetManager.registerAssetFunction(s3Bucket, "s3Bucket")
assetManager.registerAssetFunction(crawlHandler, "crawlHandler")



    
class SQLGearmanWorker(gearman.GearmanWorker):
    def on_job_execute(self, current_job):
        print >> sys.stderr, "Job started"
        return super(SQLGearmanWorker, self).on_job_execute(current_job)

    def on_job_exception(self, current_job, exc_info):
        print >> sys.stderr, "Job failed"
        print >> sys.stderr, exc_info
        return super(SQLGearmanWorker, self).on_job_exception(current_job, exc_info)

    def on_job_complete(self, current_job, job_result):
        print >> sys.stderr, "Job completed"
        print >> sys.stderr, current_job
        print >> sys.stderr, job_result
        return super(SQLGearmanWorker, self).send_job_complete(current_job, job_result)

    def after_poll(self, any_activity):
        # Return True if you want to continue polling, replaces callback_fxn
        return True

def getLimitOffset(data):
    if 'limit' in data:
        limit = data['limit']
    else:
        limit = default_page_size
    if 'offset' in data:
        offset = data['offset']
    else:
        offset = 0
    return limit, offset




def getPk(pk, row):
    pklist = []
    for idx in pk:
        nextVal = row[idx]
        pklist.append(nextVal)
    return tuple(pklist)
def verifyNameMapping(row, nameMapping):
    for name, dct in nameMapping.iteritems():
        for idx, field in dct.iteritems():
            if type(idx) != type(3):
                continue
            if idx > len(row) - 1:
                raise Exception('nameMapping invalid, index {} is out of range'.format(idx))
            if field in nameMapping:
                raise Exception('nameMapping invalid, {} is the name of a name field and a name'.format(field))


def getStarts(joinOn):
    startName = joinOn[0]['one']
    result = [0]
    for i, jo in enumerate(joinOn):
        if startName == jo['one']:
            result.append(i)
    return result



def getPkFromMapping(row, mapping):
    li = []
    anyVals = False
    for k,v in mapping.iteritems():
        if type(k) == type(23):
            li.append(row[k]) 
            if row[k]:
                anyVals = True   
    if anyVals:
        return tuple(li)
    else:
        return False

def hasSublist(mapping):
    for k,v in mapping.iteritems():
        if type(k) == type('fnord') and type(v) == type([]):
            return True
        elif type(v) == type({}):
            if hasSublist(v):
                return True
    return False

def extractIt(row, mapping, result, idxs, attrName):   
    #print 'ROW IS {}'.format(row) 
    if attrName and attrName not in idxs:
        idxs[attrName] = {}
    if type(result) == type([]):
        pk = getPkFromMapping(row, mapping)
        #print 'PK is {}, attrName is {}'.format(pk, attrName)        
        if pk and pk not in idxs[attrName]:            
            idxs[attrName][pk] = len(result)
            result.append({})    
            #print 'appended {} for PK'        
        if pk:
            pkindex = idxs[attrName][pk]
            #print 'pkindex is {}'.format(pkindex)
            #print 'into this result {}'.format(result)
            if hasSublist(mapping):
                attrName = str(pk)+attrName
            extractIt(row, mapping, result[pkindex], idxs, attrName)

    elif type(result) == type({}):
        pk = getPkFromMapping(row, mapping)
        if hasSublist(mapping):
            if not attrName:
                attrName = ''
            attrName = str(pk)+attrName
        for k,v in mapping.iteritems():
            if(type(k) == type(23)):
                if v not in result:
                    result[v] = row[k]
            elif type(k) == type('fnord'):
                if k not in result:
                    if type(v) == type({}):
                        result[k] = {}
                    elif type(v) == type([]):
                        result[k] = []
                    else:
                        raise Exception('bad name mapping for joiner')
                if type(v) == type({}):
                    extractIt(row, v, result[k], idxs, attrName)
                elif type(v) == type([]):
                    if not attrName:
                        attrName = ''
                    extractIt(row, v[0], result[k], idxs, k + attrName)
                else:
                    raise Exception('bad name mapping for joiner')
    else:
        raise Exception('bad name mapping for joiner')

    


def joinResult(rows, nameMapping):       
    result = {}
    idxs = {}
    attrName = None
    if len(nameMapping) == 1:
        key = nameMapping.keys()[0]
        if type(nameMapping[key]) == type([]):
            attrName = key
            if len(rows) == 0:
                result[key] = []
    for row in rows:
        extractIt(row, nameMapping, result, idxs, attrName)    
    #print 'joinResult result: {}'.format(result)
    return result

def extractFromRow(row, mapping):
    result = {}
    for idx, name in mapping.iteritems():
        if type(idx) == type(3):
            result[name] = row[idx]
        else:
            result[idx] = extractFromRow(row, name)
    return result


def unicodeEscape(stri):
    if type(stri) == type(u''):
        return stri
    return stri.decode('utf-8', errors='backslashreplace')

def strEscape(uni):
    if(type(uni) == type('')):
        return uni
    return uni.encode('utf-8', errors='backslashreplace')

#stack overflow http://stackoverflow.com/questions/455580/json-datetime-between-python-and-javascript
dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.datetime)  or isinstance(obj, datetime.date) else None


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

def stripIds(values):
    result = {}    
    for k,v in values.iteritems():
        if k == '_id' or k == '__v':
            continue
        if type(v) == type([]):
            newArr = []
            for val in v:
                if(type(val) == type({})):
                    newArr.append(stripIds(val))
                else:
                    newArr.append(v)
            result[k] = newArr

        if type(v) == type({}):
            result[k] = stripIds(v)
        else:
            result[k] = v
    return result

def postData(endpoint, values):
    values = stripIds(values)
    for k, v in values.iteritems():
        if type(v) == type([]):
            v = json.dumps(v)
        elif type(v) == type({}):
            v = json.dumps(v)        
        values[k] = unicode(v).encode('utf-8')    
    data = urllib.urlencode(values)
    req = urllib2.Request(endpoint, data)
    response = urllib2.urlopen(req)
    return response.read()

def extractPost(url, post_rule):
    result = {
        'title': '',
        'byline': '',
        'post_date': '',        
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
        result['content'] = s_content.__repr__()
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

    