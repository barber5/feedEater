import json, traceback, sys, redis, uuid, datetime
from config import redisCfg

pool = redis.ConnectionPool(host=redisCfg['host'], port=redisCfg['port'])

class AccessException(Exception):
	def __init__(self, value=""):
		self.value = value
	def __str__(self):
		return repr(self.value)

class AssetException(Exception):
	def __init__(self, value=""):
		self.value = value
	def __str__(self):
		return repr(self.value)

class AssetManager:
	def __init__(self, assetFuncs={}):
		self.assetFuncs = assetFuncs
		self.assetCache = {}
	def getAsset(self, k, v):
		print 'getting asset for {}'.format(k)
		if type(v) != type({}):
			return v
		if 'cached' in v and v['cached'] and k in self.assetCache:
			return self.assetCache[k]
		if k not in self.assetFuncs:
			raise Exception('key {} not in assetFuncs'.format(k))
		else:
			result = self.assetFuncs[k](v)
			if 'cacheAsset' in v and v['cacheAsset']:
				self.assetCache[k] = result
			return result
	def registerAssetFunction(self, fun, name):
		self.assetFuncs[name] = fun


'''
first check user level deny
then user level allow
then group level deny
then group level allow
then all deny/allow
@access(allAllow=False, allDeny=False, groupAllow=['GUEST', 'ETHEAN'], groupDeny=['BANNED', '#community_id:ADMIN'], userDeny=[], userAllow=[#ethean_id])
'''
class AccessManager:
	def __init__(self, accessFuncs={}):
		self.accessFuncs = accessFuncs
		self.admin_ids = {}

	def hasAdminAccess(self, userData):
		return True

	def groupAllow(self, userData, kwargs):
		None

	def groupDeny(self, userData, kwargs):
		None

	def userAllow(self, userData, kwargs):
		None

	def userDeny(self, userData, kwrags):
		None

	def access(self, userData, kwargs):
		# first put superuser tests
		if self.hasAdminAccess(userData):
			return True
		if self.userDeny(userData, kwargs):
			return False
		if self.userAllow(userData, kwargs):
			return True
		if self.groupDeny(userData, kwargs):
			return False
		if self.groupAllow(userData, kwargs):
			return True
		if 'allDeny' in kwargs and kwargs['allDeny']:
			return False
		if 'allAllow' in kwargs and kwargs['allAllow']:
			return True		
		else:
			return False

def assets(**kwargs):
	print 'asset decorator begin'
	print 'asset decorator kwargs: {}'.format(kwargs)		
	def wrap(f):
		print 'asset decorator outer wrapper begin'						
		if len(kwargs) > 0 and 'assetManager' in kwargs:
			def wrapped_f(*args):
				print 'asset decorator inner wrapper begin'
				myAssets = {}				
				am = kwargs['assetManager']					
				for k,v in kwargs.iteritems():
					if k == 'assetManager':
						continue
					myAssets[k] = am.getAsset(k, v)
				result = f(*args, assets=myAssets)
				for asset in myAssets:
					if 'cleanup' in dir(myAssets[asset]):
						myAssets[asset].cleanup()
				return result
				print 'asset decorator inner wrapper end'
			print 'asset decorator outer wrapper end'		
			return wrapped_f
		else:
			def wrapped_f(*args):
				print 'asset decorator inner wrapper begin'
				result = f(*args)
				print 'asset decorator inner wrapper end'
				return result
			print 'asset decorator outer wrapper end'		
			return wrapped_f
	print 'asset decorator end'
	return wrap


xforms = {
	type(uuid.uuid4()) : lambda x : str(x),
	type(datetime.datetime.now()): lambda x: x.isoformat()
}

def sanitize_list(lis):	
	for i, li in enumerate(lis):
		if type(li) in xforms:
			lis[i] = xforms[type(li)](li)
		elif type(li) == type([]):
			lis[i] = sanitize_list(li)
		elif type(li) == type({}):
			lis[i] = sanitize_result(li)
	return lis

def sanitize_result(res):		
	for k,v in res.iteritems():
		if type(v) in xforms:			
			res[k] = xforms[type(v)](v)
		if(type(v) == type([])):
			res[k] = sanitize_list(v)
		if(type(v) == type({})):
			res[k] = sanitize_result(v)
	return res

def gearman_worker_func(f):
	print 'gearman decorator begin'
	def wrapped(gearman_worker, job, **kwargs):		
		print 'gearman inner wrapper begin'
		data = json.loads(job.data)
		try:
			if 'assets' in kwargs:
				result = f(data, assets=kwargs['assets'])
			else:
				result = f(data)
			print 'gearman_worker_func result: {}'.format(result)
			result = sanitize_result(result)
			return json.dumps(result)		
		except AccessException as e:
			print >> sys.stderr, unicode(e)+'\ntraceback: '+unicode(traceback.format_exc())
			return json.dumps({'error':'no permission'})
		except AssetException as e:			
			print >> sys.stderr, unicode(e)+'\ntraceback: '+unicode(traceback.format_exc())
			return json.dumps({'error':'asset error'})
		except:
			print >> sys.stderr, unicode(sys.exc_info()[0])+'\ntraceback: '+unicode(traceback.format_exc())		
	print 'gearman decorator end'
	return wrapped

def access(**kwargs):	
	print 'access decorator begin'
	print 'access decorator kwargs: {}'.format(kwargs)			
	def a_wrap(f):
		print 'access decorator outer wrapper begin'
		@gearman_worker_func
		def wrapped_f(data, **kwargs2):
			print 'access decorator inner wrapper begin'
			print 'access data: {}'.format(data)
			# populate the access object from the access token
			client = redis.Redis(connection_pool=pool)
			if 'access_token' in data:	
				redisData = client.hget('access', data['access_token'])
				if redisData:
					userData = json.loads(redisData)
				else:
					userData = {}									
			else:
				userData = {}
			if 'accessManager' in kwargs and kwargs['accessManager'].access(userData, kwargs):
				if 'assets' in kwargs2:
					return f(userData, data, assets=kwargs2['assets'])
				else:
					return f(userData, data)	
			else: 
				raise AccessException()
			print 'access decorator inner wrapper end'
		return wrapped_f
		print 'access decorator outer wrapper end'
	print 'access decorator end'
	return a_wrap
