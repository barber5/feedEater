import mechanize, sys, traceback, urllib, urllib2, json
from bs4 import NavigableString, Comment
import gearman, redis, os, sys, psycopg2, traceback, smtplib
from access import AssetManager, AccessManager, AssetException
import smtplib, json, datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config import default_page_size

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

class EmailWrap():
    def __init__(self, cfg):
        s = smtplib.SMTP(host=cfg['host'], port=cfg['port'])
        s.ehlo()
        s.starttls()
        s.set_debuglevel(True)
        s.login(cfg['email'], cfg['pass'])
        self.smtp = s

    def send_greeting(self, to, token):
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Welcome to Ethea"
        msg['From'] = 'Ethea'
        msg['To'] = 'New Ethean'

        # Create the body of the message (a plain-text and an HTML version).
        text = "Hi!\nHere is the link you wanted:\nhttp://ec2-54-193-33-113.us-west-1.compute.amazonaws.com:3000/verify_email?email=%s&email_token=%s" % (to, token)
        html = """\
        <html>
          <head></head>
          <body>
            <p>Hi!<br>               
               Here is the <a href="http://ec2-54-193-33-113.us-west-1.compute.amazonaws.com:3000/verify_email?email=%s&email_token=%s">link</a> you wanted.
            </p>
          </body>
        </html>
        """ % (to, token)

        # Record the MIME types of both parts - text/plain and text/html.
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')

        # Attach parts into message container.
        # According to RFC 2046, the last part of a multipart message, in this case
        # the HTML message, is best and preferred.
        msg.attach(part1)
        msg.attach(part2)
        self.smtp.sendmail(default_from_email, to, msg.as_string())

    def send_resetpw(self, to, token):
        None

    def cleanup(self):
        self.smtp.quit()

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

def email(cfg):
    if 'host' not in cfg or 'port' not in cfg or 'email' not in cfg or 'pass' not in cfg:
        raise AssetException()    
    return EmailWrap(cfg)

assetManager = AssetManager()
assetManager.registerAssetFunction(redisPool, "redisPool")
assetManager.registerAssetFunction(dbCursor, "dbCursor")
assetManager.registerAssetFunction(s3Bucket, "s3Bucket")
assetManager.registerAssetFunction(email, 'email')


    
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