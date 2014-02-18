import gearman
import json
import uuid
import datetime
import traceback



def do_insert(cursor, tableName, data, returnQuery=False, ignoreFields={}):
    print 'do_insert'
    query = 'INSERT INTO %s (' % tableName
    values = ' VALUES('
    setValues = []
    for key, value in data.iteritems():
        if key in ignoreFields or (key=='access_token' and '-access_token' not in ignoreFields):
            continue
        if type(value) == type({}) or type(value) == type([]):
            continue  
        if value=='':
            None                 
        if(type(value) == type(uuid.uuid4())):
            setValues.append(str(value))
        else:    
            setValues.append(value)            
        query += '%s, ' % key
        values += '%s, '    
    query = query[:-2] + ')' + values[:-2] + ');'
    print cursor.mogrify(query, setValues)    
    if returnQuery:
        query = cursor.mogrify(query, setValues)                             
        return query         
    cursor.execute(query, setValues)
    

def do_exists(cursor, tableName, conditions, returnQuery=False):
    query = 'SELECT exists (SELECT 1 FROM %s WHERE ' % tableName
    print conditions
    vals = []
    for k,v in conditions.iteritems():
        query += k + '=%s AND '
        vals.append(v)
    if len(conditions) > 0:
        query = query[:-5]
    query += ' LIMIT 1);'    
    cursor.execute(query, vals)
    exists = cursor.fetchone()    
    if "t" in str(exists).lower():
         return True
    return False

def new_object(cursor, tableName, data, newUUID=None, returnQuery=False, ignoreFields={}):    
    if not newUUID:
        newUUID = uuid.uuid4()

    data['id'] = str(newUUID)
    now = str(datetime.datetime.now())
    data['created'] = now
    data['updated'] = now    
    
    if returnQuery:
        query = do_insert(cursor, tableName, data, True, ignoreFields)
        return query     
    
    do_insert(cursor, tableName, data, False)
    
    return str(newUUID)
                
def new_relation(cursor, tableName, data, returnQuery=False, timeStamp=False, ignoreFields={}):    
    if timeStamp:
        now = str(datetime.datetime.now())    
        data['created'] = now
        data['updated'] = now
    if returnQuery:
        query = do_insert(cursor, tableName, data, returnQuery=True, ignoreFields=ignoreFields)
        return query
    do_insert(cursor, tableName, data, returnQuery=returnQuery, ignoreFields=ignoreFields)

def update_object(cursor, tableName, idName, data, returnQuery=False, ignoreFields={}):                    
        setValues = "UPDATE %s SET " % tableName
        vals = []
        for key, value in data.iteritems():
            if key in ignoreFields or (key=='access_token' and '-access_token' not in ignoreFields):
                continue
            if type(value) == type({}) or type(value) == type([]):
                continue                       
            if(key!=idName):
                setValues = setValues + key+"=%s, "
                if(type(value) == type(uuid.uuid4())):                    
                    vals.append(str(value))
                else:                                            
                    vals.append(value)
                        
        query = setValues + " updated=%s WHERE id=%s;"
        now = str(datetime.datetime.now())
        if returnQuery:
            query = cursor.mogrify(query, vals + [now, data[idName]])
            return query
        print cursor.mogrify(query, vals + [now, data[idName]])
        cursor.execute(query, vals + [now, data[idName]])

def update_relation(gearman_worker, job, tableName, returnQuery=False):
    try:        
        data = json.loads(job.data)
        conn = psycopg2.connect(database=d, user=u, host=h, port=p)
        cur = conn.cursor()
        setValues = ""
        vals = []
        for key, value in data.iteritems():
            if type(value) == type({}) or type(value) == type([]):
                continue
            if(key!=idName):
                if(type(value) == type(uuid.uuid4())):
                    setValues = setValues + "%s='"+str(value)+"', "
                    vals.append(key)
                else:    
                    setValues = setValues + "%s=%s, "
                    vals.append(key)
                    vals.append(value)
        setValues = setValues[:-1]
        query = "UPDATE " + tableName + " SET " + setValues + " updated='" + str(datetime.datetime.now()) + "' " + "WHERE id='" + data[idName] + "';"        
        if returnQuery:
            query = cursor.mogrify(query, vals)
            return query
        cursor.execute(query, vals)
        
        conn.commit()
        
        return json.dumps({"status":"OK"})
    except Exception as e:
        if returnQuery:
            raise e
        print unicode(e)+'\ntraceback: '+unicode(traceback.format_exc())
        return json.dumps({"status":"error", "result":"", "error":unicode(e)})
    finally:
        if cur:
            cursor.close()
        if conn:
            conn.close()

def remove_relation(cur, tableName, data, returnQuery=False, ignoreFields={}):
    query = "DELETE FROM " + tableName + " WHERE "                        
    setValues = []
    for key, value in data.iteritems(): 
        if key in ignoreFields or (key=='access_token' and '-access_token' not in ignoreFields):
            continue
        if type(value) == type({}) or type(value) == type([]):
            continue   
        query += key+'=%s AND '
        setValues.append(value)    
    query = query[:-5]
    if returnQuery:
        query = cur.mogrify(query, setValues)
        return query
    cur.execute(query, setValues)        

def new_transaction(cursor, statmentList):
    query = "BEGIN; "
    for stmt in statmentList:               
        print len(stmt)
        query += '\n\n%s \n\n' % stmt
    query += "COMMIT;"    
    print query          
    cursor.execute(query)                
        

def delete_object(cursor, tableName, columnName, columnValue, returnQuery=False):    
    delete_query = "DELETE FROM %s" % tableName
    delete_query += " WHERE %s=" % columnName
    delete_query += '%s;'
    if returnQuery:
        return cursor.mogrify(delete_query, [columnValue])
    print cursor.mogrify(delete_query, [columnValue])

    cursor.execute(delete_query, [columnValue])    

