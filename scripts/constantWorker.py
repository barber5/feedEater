from util import SQLGearmanWorker
from util import assetManager
from config import redisCfg, dbCfg, s3Cfg, default_page_size, crawlCfg
import pprint, json, redis, time, urlparse
from random import random

cur = assetManager.getAsset('dbCursor', dbCfg)
ch = assetManager.getAsset('crawlHandler', crawlCfg)
client = assetManager.getAsset('redisPool', redisCfg)

def crawl_work_much(userData, data, assets):			
	resId = None
	domain = None	
	
	while True:
		print ch.doWork(client, cur, resId=resId, domain=domain)
		time.sleep(1)

if __name__ == "__main__":
	crawl_work_much()