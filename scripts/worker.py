from util import SQLGearmanWorker
from access import access, assets, AccessManager
from util import assetManager, SQLGearmanWorker, getLimitOffset, joinResult
from config import redisCfg, dbCfg, s3Cfg, default_page_size
from db import new_object, do_exists, new_transaction, update_object, delete_object, new_relation, remove_relation
from uuid import uuid4
import pprint

@assets(assetManager=assetManager, dbCursor=dbCfg)
@access(accessManager=AccessManager())
def new_itemtype(userData, data, assets):        
    newUUID = new_object(assets['dbCursor'], 'itemtypes', data)
    return {'itemtype_id': newUUID}


SQLworker = SQLGearmanWorker(['localhost:4730'])
SQLworker.register_task("new_itemtype", new_itemtype)