from util import SQLGearmanWorker
from access import access, assets, AccessManager
from util import assetManager, SQLGearmanWorker, getLimitOffset, joinResult
from config import redisCfg, dbCfg, s3Cfg, default_page_size, crawlCfg
from db import new_object, do_exists, new_transaction, update_object, delete_object, new_relation, remove_relation
from uuid import uuid4
import pprint, json, redis, time, urlparse
from random import random
from postExtractor import extractPosts, extractPost, getNextPage
from bs4 import NavigableString, Comment, BeautifulSoup as bs


@assets(assetManager=assetManager, dbCursor=dbCfg,crawlHandler=crawlCfg, redisPool=redisCfg)
@access(accessManager=AccessManager())
def init_feed(userData, data, assets):     
	print data
	ch = assets['crawlHandler']
	client = redis.Redis(connection_pool=assets['redisPool'])
	cur = assets['dbCursor']
	ch.addCrawl(data['feed_id'], 'feed', client, cur)
	return {}



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
	resId = None
	domain = None
	if 'resId' in data:
		resId = data['resId']
	if 'domain' in data:
		domain = data['domain']


	
	result.append(ch.doWork(client, cur, resId=resId, domain=domain))
		
	return {'work': result}


@assets(assetManager=assetManager, dbCursor=dbCfg,crawlHandler=crawlCfg, redisPool=redisCfg)
@access(accessManager=AccessManager())
def crawl_work_much(userData, data, assets):	
	return {}
	print data
	ch = assets['crawlHandler']
	client = redis.Redis(connection_pool=assets['redisPool'])
	cur = assets['dbCursor']
	result = []
	resId = None
	domain = None
	if 'resId' in data:
		resId = data['resId']
	if 'domain' in data:
		domain = data['domain']

	
	for i in range(1000):		
		result.append(ch.doWork(client, cur, resId=resId, domain=domain))
		time.sleep(1)
		
	return {'work': result}


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
		'postlist': data['postlist'],
		'comment': data['comment']
	}
	page_rule = data['pagination']	
	posts = extractPosts(post_rule, blog_url)
	result = {}
	result['homepage'] = posts
	pages = [blog_url]
	np = urlparse.urljoin(blog_url, getNextPage(page_rule, blog_url, pages))
	print 'next pge is {}'.format(np)
	posts = (extractPosts(post_rule, np))	
	result['page2'] = posts	
	np = urlparse.urljoin(np, getNextPage(page_rule, np, pages))
	pages.append(np)
	posts = extractPosts(post_rule, np)
	pages.append(np)
	result['page3'] = posts		
	if len(posts) > 0:
		result['typical_post'] = extractPost(posts[0], post_rule, post_rule['comment'])		
		
	return result		

@assets(assetManager=assetManager, dbCursor=dbCfg)
@access(accessManager=AccessManager())
def feed_links(userData, data, assets):
	cur = assets['dbCursor']
	query = "SELECT po.id, po.title, po.content, po.post_url from posts po where po.title is not null and po.feed_id=%s limit 20"	
	nameMapping = {
		'posts': [{
			0: 'post_id',
			1: 'title',
			2: 'content',
			3: 'post_url'
		}]
	}
	posts = cur.select(query, [data['feed_id']], nameMapping)
	print len(posts['posts'])
	result = {'links': []}
	for p in posts['posts']:
		html = p['content']
		soup = bs(html)
		links = soup.find_all('a')
		for link in links:					
			if 'href' not in link.attrs:
				continue
			print urlparse.urljoin(p['post_url'], link.attrs['href'])
			result['links'].append(urlparse.urljoin(p['post_url'], link.attrs['href']))
	return result

@assets(assetManager=assetManager, dbCursor=dbCfg)
@access(accessManager=AccessManager())
def feed_quotes(userData, data, assets):
	cur = assets['dbCursor']
	query = "SELECT po.id, po.title, po.content from posts po where po.title is not null and po.feed_id=%s"	
	nameMapping = {
		'posts': [{
			0: 'post_id',
			1: 'title',
			2: 'content'
		}]
	}
	posts = cur.select(query, [data['feed_id']], nameMapping)
	result = {'links': []}
	for p in posts['posts']:
		html = p['content']
		soup = bs(html)
		links = soup.find_all('blockquote')
		for link in links:			
			result['links'].append(link)
	return result


SQLworker = SQLGearmanWorker(['localhost:4730'])
SQLworker.register_task("init_feed", init_feed)
SQLworker.register_task("crawl_all", crawl_all)
SQLworker.register_task("crawl_work", crawl_work)
SQLworker.register_task("crawl_work_much", crawl_work_much)
SQLworker.register_task("crawl_post", crawl_post)
SQLworker.register_task("test_rule", test_rule)
SQLworker.register_task("feed_links", feed_links)
SQLworker.register_task("feed_quotes", feed_quotes)

SQLworker.work()