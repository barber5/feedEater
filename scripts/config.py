import os
domain = 'ec2-54-193-7-229.us-west-1.compute.amazonaws.com'
default_page_size = 50
default_autocomplete_page_size = 20


def getEnv(key, default):
    if key in os.environ:
        print 'found key %s, setting %s' % (key, os.environ[key])
        return os.environ[key]
    else:
        print 'did not find key %s, setting default %s' % (key, default)
        return default

redisCfg = {
    'host' : getEnv('REDIS_SERVER', 'localhost'),
    'port' : getEnv('REDIS_PORT', 6379)
}

dbCfg = {
    'database'  : getEnv('DATABASE', 'feed_eater'),
    'password'  : 'feedpass',
    'user'      : getEnv('DB_USER', 'feedman'),
    'host'      : getEnv('DB_HOST', domain),
    'port'      : getEnv('DB_PORT', 5432)
}

s3Cfg = {
    'access'    : getEnv('AWS_ACCESS_KEY_ID', 'AKIAJ2ZCFGJ7FR6QXSSQ'), 
    'secret'    : getEnv('AWS_SECRET_ACCESS_KEY', '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'),
    'bucketName': getEnv('S3_BUCKET', 'feedimages')
}

crawlCfg = {
    'crawlHash': 'crawl',
    'domainHash': 'domain',
    'crawlDelay': 5,
    'randomDelay': 15 # delay is crawlDelay + random(randomDelay)
}

