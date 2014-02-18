from util import SQLGearmanWorker
from access import access, assets, AccessManager
from util import assetManager, SQLGearmanWorker, getLimitOffset, joinResult
from config import redisCfg, dbCfg, s3Cfg, default_page_size, crawlCfg
from db import new_object, do_exists, new_transaction, update_object, delete_object, new_relation, remove_relation
from uuid import uuid4
import pprint, json, redis, time, urlparse
from random import random
from postExtractor import extractPosts, extractPost, getNextPage

@assets(assetManager=assetManager, dbCursor=dbCfg, redisPool=redisCfg, crawlHandler=crawlCfg)
@access(accessManager=AccessManager())
def new_feed(userData, data, assets):        
    newUUID = new_object(assets['dbCursor'], 'feeds', data)    
    return {'feed_id': newUUID}

@assets(assetManager=assetManager, dbCursor=dbCfg, redisPool=redisCfg, crawlHandler=crawlCfg)
@access(accessManager=AccessManager())
def new_category(userData, data, assets):        
    newUUID = new_object(assets['dbCursor'], 'categories', data)    
    return {'category_id': newUUID}

@assets(assetManager=assetManager, dbCursor=dbCfg,crawlHandler=crawlCfg, redisPool=redisCfg)
@access(accessManager=AccessManager())
def init_feed(userData, data, assets):     
	print data
	ch = assets['crawlHandler']
	client = redis.Redis(connection_pool=assets['redisPool'])
	cur = assets['dbCursor']
	ch.addCrawl(data['feed_id'], 'feed', client, cur)
	return {}

@assets(assetManager=assetManager, dbCursor=dbCfg)
@access(accessManager=AccessManager())
def feed_rules(userData, data, assets):
	print data
	feedId = data['feed_id']
	del data['feed_id']	
	pagination = data['pagination']
	del data['pagination']
	rulesData = {
		'feed_id': feedId,
		'pagination_rule': pagination,
		'extraction_rule': json.dumps(data)
	}
	update_object(assets['dbCursor'], 'feeds', 'feed_id', rulesData)
	return {}
@assets(assetManager=assetManager, dbCursor=dbCfg)
@access(accessManager=AccessManager())
def all_feeds(userData, data, assets):     
	cur = assets['dbCursor']
	query = "SELECT fe.id, fe.name, fe.feed_url, fe.blog_url, fe.extraction_rule, fe.pagination_rule, fe.last_crawl, fe.created, fe.updated,(select count(*) FROM posts where feed_id=fe.id) as pcount, (select count(*) FROM posts where feed_id=fe.id and title is not null) as crawled FROM feeds as fe";
	cur.execute(query, [])
	rows = cur.fetchall()
	nameMapping = {
		'feeds': [{
			0: 'id',
			1: 'name',
			2: 'feed_url',
			3: 'blog_url',
			4: 'extraction_rule',
			5: 'pagination_rule',
			6: 'last_crawl',
			7: 'created',
			8: 'updated',
			9: 'total',
			10: 'crawled'
		}]
	}
	result = joinResult(rows, nameMapping)
	return result
@assets(assetManager=assetManager, dbCursor=dbCfg)
@access(accessManager=AccessManager())
def get_feed(userData, data, assets):
	cur = assets['dbCursor']
	query = "SELECT id, name, feed_url, blog_url, extraction_rule, pagination_rule, last_crawl, created, updated FROM feeds where id=%s";
	cur.execute(query, [data['feed_id']])
	rows = cur.fetchall()
	nameMapping = {
		'feed': {
			0: 'id',
			1: 'name',
			2: 'feed_url',
			3: 'blog_url',
			4: 'extraction_rule',
			5: 'pagination_rule',
			6: 'last_crawl',
			7: 'created',
			8: 'updated'
		}
	}
	result = joinResult(rows, nameMapping)
	return result

@assets(assetManager=assetManager, dbCursor=dbCfg)
@access(accessManager=AccessManager())
def all_categories(userData, data, assets):
	cur = assets['dbCursor']
	query = "SELECT id, name FROM categories";
	cur.execute(query, [])
	rows = cur.fetchall()
	nameMapping = {
		'categories': [{
			0: 'id',
			1: 'name'			
		}]
	}
	result = joinResult(rows, nameMapping)
	return result

# crawl a single post for a feed
@assets(assetManager=assetManager, dbCursor=dbCfg,crawlHandler=crawlCfg, redisPool=redisCfg)
@access(accessManager=AccessManager())
def crawl_post(userData, data, assets):
	print data
	ch = assets['crawlHandler']
	client = redis.Redis(connection_pool=assets['redisPool'])
	cur = assets['dbCursor']
	ch.addCrawl(data['post_id'], 'post', client, cur)
	return {}



# crawl all posts that have been loaded in for a feed in the crawl_feed above
@assets(assetManager=assetManager, dbCursor=dbCfg, crawlHandler=crawlCfg, redisPool=redisCfg)
@access(accessManager=AccessManager())
def crawl_all(userData, data, assets):	
	cur = assets['dbCursor']
	client = redis.Redis(connection_pool=assets['redisPool'])
	ch = assets['crawlHandler']
	print data
	query = "SELECT id FROM posts where feed_id=%s and title is null"	
	cur.execute(query, [data['feed_id']])
	rows = cur.fetchall()
	nameMapping = {
		'posts': [{
			0: 'post_id'
		}]
	}
	posts = joinResult(rows, nameMapping)	
	for p in posts['posts']:
		print 'adding to crawl queue'
		print p
		ch.addCrawl(p['post_id'], 'post', client, cur)
	return {}
	

@assets(assetManager=assetManager, dbCursor=dbCfg,crawlHandler=crawlCfg, redisPool=redisCfg)
@access(accessManager=AccessManager())
def crawl_work(userData, data, assets):
	print data
	ch = assets['crawlHandler']
	client = redis.Redis(connection_pool=assets['redisPool'])
	cur = assets['dbCursor']
	result = []
	for i in range(15):
		result.append(ch.doWork(client, cur))
		time.sleep(.1)
	return {'work': result}

@assets(assetManager=assetManager, dbCursor=dbCfg, crawlHandler=crawlCfg, redisPool=redisCfg)
@access(accessManager=AccessManager())
def get_jobs(userData, data, assets):
	ch = assets['crawlHandler']
	client = redis.Redis(connection_pool=assets['redisPool'])
	cur = assets['dbCursor']
	return {'jobs': ch.getWorkStats(client, cur)}

@assets(assetManager=assetManager, dbCursor=dbCfg)
@access(accessManager=AccessManager())
def get_posts(userData, data, assets):
	cur = assets['dbCursor']
	query = "SELECT id, title, byline, post_date, post_url FROM posts where feed_id=%s"
	cur.execute(query, [data['feed_id']])
	rows = cur.fetchall()
	nameMapping = {
		'posts': [{
			0: 'post_id',
			1: 'title',
			2: 'byline',
			3: 'post_date',
			4: 'post_url'
		}]
	}
	posts = joinResult(rows, nameMapping)	
	return posts
@assets(assetManager=assetManager, dbCursor=dbCfg)
@access(accessManager=AccessManager())
def get_post(userData, data, assets):
	cur = assets['dbCursor']
	query = "SELECT po.id, po.title, po.byline, po.post_date, po.post_url, po.content, fe.name FROM posts po inner join feeds fe on fe.id=po.feed_id where po.id=%s"
	cur.execute(query, [data['post_id']])
	rows = cur.fetchall()
	nameMapping = {
		'posts': [{
			0: 'post_id',
			1: 'title',
			2: 'byline',
			3: 'post_date',
			4: 'post_url',
			6: 'feed',
			5: 'content'

		}]
	}
	posts = joinResult(rows, nameMapping)	
	return posts


@assets(assetManager=assetManager, dbCursor=dbCfg)
@access(accessManager=AccessManager())
def test_rule(userData, data, assets):
	cur = assets['dbCursor']
	query = "SELECT blog_url, extraction_rule, pagination_rule FROM feeds where id=%s"
	cur.execute(query, [data['feed_id']])
	rows = cur.fetchall()
	blog_url = rows[0][0]
	post_rule = {
		'title': data['title'],
		'byline': data['byline'],
		'post_date': data['post_date'],
		'content': data['content'],
		'postlist': data['postlist']
	}
	page_rule = data['pagination']	
	posts = extractPosts(post_rule, blog_url)
	result = {}
	result['homepage'] = posts
	np = urlparse.urljoin(blog_url, getNextPage(page_rule, blog_url))
	posts = (extractPosts(post_rule, np))	
	result['page2'] = posts	
	np = urlparse.urljoin(np, getNextPage(page_rule, np))
	posts = extractPosts(post_rule, np)
	result['page3'] = posts		
	if len(posts) > 0:
		result['typical_post'] = extractPost(posts[0], post_rule)
	return result		


SQLworker = SQLGearmanWorker(['localhost:4730'])
SQLworker.register_task("init_feed", init_feed)
SQLworker.register_task("crawl_all", crawl_all)
SQLworker.register_task("crawl_work", crawl_work)


SQLworker.work()