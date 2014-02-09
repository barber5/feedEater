from util import SQLGearmanWorker
from access import access, assets, AccessManager
from util import assetManager, SQLGearmanWorker, getLimitOffset, joinResult
from config import redisCfg, dbCfg, s3Cfg, default_page_size, crawlCfg
from db import new_object, do_exists, new_transaction, update_object, delete_object, new_relation, remove_relation
from uuid import uuid4
import pprint, json
import time
from random import random

@assets(assetManager=assetManager, dbCursor=dbCfg)
@access(accessManager=AccessManager())
def new_feed(userData, data, assets):        
    newUUID = new_object(assets['dbCursor'], 'feeds', data)
    return {'feed_id': newUUID}

@assets(assetManager=assetManager, dbCursor=dbCfg,crawlHandler=crawlCfg, redisPool=redisCfg)
@access(accessManager=AccessManager())
def init_feed(userData, data, assets):     
	ch = assets['crawlHandler']
	client = redis.Redis(connection_pool=assets['redisPool'])
	cur = assets['dbCursor']
	ch.addCrawl(data['feedId'], 'feed', client, cur)
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
	query = "SELECT id, name, feed_url, blog_url, extraction_rule, pagination_rule, last_crawl, created, updated FROM feeds";
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
			8: 'updated'
		}]
	}
	result = joinResult(rows, nameMapping)
	return result

# crawl a single post for a feed
@assets(assetManager=assetManager, dbCursor=dbCfg)
@access(accessManager=AccessManager())
def crawl_post(userData, data, assets):
	None

# crawl all posts that have been loaded in for a feed in the crawl_feed above
@assets(assetManager=assetManager, dbCursor=dbCfg)
@access(accessManager=AccessManager())
def crawl_all_posts(userData, data, assets):
	None


SQLworker = SQLGearmanWorker(['localhost:4730'])
SQLworker.register_task("new_feed", new_feed)
SQLworker.register_task("all_feeds", all_feeds)
SQLworker.register_task("init_feed", init_feed)
SQLworker.register_task("feed_rules", feed_rules)

SQLworker.work()