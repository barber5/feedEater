import os

default_page_size = 50
default_autocomplete_page_size = 20

default_from_email = 'SMTPTEST123456789@gmail.com'

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
    'host'      : getEnv('DB_HOST', 'localhost'),
    'port'      : getEnv('DB_PORT', 5432)
}

s3Cfg = {
    'access'    : getEnv('AWS_ACCESS_KEY_ID', 'AKIAJ2ZCFGJ7FR6QXSSQ'), 
    'secret'    : getEnv('AWS_SECRET_ACCESS_KEY', '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'),
    'bucketName': getEnv('S3_BUCKET', 'feedimages')
}

emailCfg = {
    'host'      : 'smtp.gmail.com',
    'port'      : 587,
    'email'     : default_from_email,
    'pass'      : "ethea123"
}