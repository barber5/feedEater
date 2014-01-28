from util import SQLGearmanWorker
from access import access, assets, AccessManager
from util import assetManager, SQLGearmanWorker, getLimitOffset, joinResult
from config import redisCfg, dbCfg, s3Cfg, default_page_size
from db import new_object, do_exists, new_transaction, update_object, delete_object, new_relation, remove_relation
from uuid import uuid4
from postExtractor import extractPosts, getNextPage, extractPost
import pprint
import time
from random import random

@assets(assetManager=assetManager, dbCursor=dbCfg)
@access(accessManager=AccessManager())
def new_feed(userData, data, assets):        
    newUUID = new_object(assets['dbCursor'], 'feeds', data)
    return {'feed_id': newUUID}

@assets(assetManager=assetManager, dbCursor=dbCfg)
@access(accessManager=AccessManager())
def crawl_blog(userData, data, assets):     
	cur = assets['dbCursor']
	query = "SELECT extraction_rule, pagination_rule, blog_url, post_url FROM feeds left outer join posts on feeds.id=posts.feed_id where id=%s"
	cur.execute(query, data['feed_id'])
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
	postUrls = extractPosts(dbResult['blog']['extraction_rule'], dbResult['blog']['blog_url'])
	newPosts = []
	postsToGrab = set([])
	for pu in postUrls:
		if pu not in dbResult['blog']['posts']:
			newPosts.append(pu)
	lastPage = dbResult['blog']['blog_url']
	while len(newPosts) > 0:
		postsToGrab = postsToGrab | set(newPosts)
		newPosts = []
		nextPage = getNextPage(dbResult['blog']['pagination_rule'], lastPage)
		if not nextPage:
			break
		postUrls = extractPosts(dbResult['blog']['extraction_rule'], nextPage)
		for pu in postUrls:
			if pu not in dbResult['blog']['posts'] and pu not in postsToGrab:
				newPosts.append(pu)
				postData = {
					'feed_id': data['feed_id'],
					'post_url': pu
				}
				new_object(cur, 'posts', postData)
		lastPage = nextPage
		time.sleep(5+20*random())
	print postsToGrab

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


SQLworker = SQLGearmanWorker(['localhost:4730'])
SQLworker.register_task("new_feed", new_feed)
SQLworker.register_task("all_feeds", all_feeds)
SQLworker.register_task("crawl_blog", crawl_blog)

SQLworker.work()