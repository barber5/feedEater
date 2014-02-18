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

@assets(assetManager=assetManager, dbCursor=dbCfg)
@access(accessManager=AccessManager())
def feed_rules(userData, data, assets):
	print data
	feedId = data['feed_id']
	del data['feed_id']	
	pagination = data['pagination']
	del data['pagination']
	rulesData = {}
	if 'blogroll' in data:
		rulesData['blogroll_rule'] = data['blogroll']
		del data['blogroll']
	if 'comment' in data:		
		rulesData['comments_rule'] = data['comment']
		del data['comment']
	rulesData['pagination_rule'] = pagination

	rulesData['feed_id'] = feedId
	rulesData['extraction_rule'] = json.dumps(data)		

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
	query = "SELECT id, name, feed_url, blog_url, extraction_rule, pagination_rule, last_crawl, created, updated, comments_rule FROM feeds where id=%s";
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
			8: 'updated',
			9: 'comments_rule'
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




SQLworker = SQLGearmanWorker(['localhost:4730'])
SQLworker.register_task("new_feed", new_feed)
SQLworker.register_task("all_feeds", all_feeds)
SQLworker.register_task("get_feed", get_feed)
SQLworker.register_task("all_categories", all_categories)
SQLworker.register_task("feed_rules", feed_rules)
SQLworker.register_task("get_jobs", get_jobs)
SQLworker.register_task("get_posts", get_posts)
SQLworker.register_task("get_post", get_post)
SQLworker.register_task("new_category", new_category)


SQLworker.work()