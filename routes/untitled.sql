SELECT DISTINCT i1.cid2 AS cid_norm, s1.cui AS cui_norm, s1.str AS str_norm, i2.cid1 AS cid_exp, s2.cui AS cui_exp, s2.str AS str_exp, t1.tid as tid_exp
  FROM terminology3.str2cid s1, terminology3.str2cid s2, terminology3.isaclosure i1, terminology3.isaclosure i2, terminology3.tid2cid t1
  WHERE i2.cid1 = s2.cid 
  AND i1.cid2 = s1.cid 
  AND i2.cid2 = i1.cid1 
  AND i2.cid1 = t1.cid
  AND s1.cui IN ('C0036202');



  SELECT DISTINCT count(mg.nid), t1.tid as tid 
  FROM stride5.mgrep mg, terminology3.str2tid t1 
  WHERE t1.tid in (SELECT DISTINCT t1.tid as tid_exp
  	FROM terminology3.str2cid s1, terminology3.str2cid s2, terminology3.isaclosure i1, terminology3.isaclosure i2, terminology3.tid2cid t1
  	WHERE i2.cid1 = s2.cid 
  	AND i1.cid2 = s1.cid 
  	AND i2.cid2 = i1.cid1 
  	AND i2.cid1 = t1.cid
  	AND s1.cui IN ('C0036202'))
  AND mg.tid=t1.tid group by tid;



  SELECT DISTINCT count(mg.nid), t1.tid as tid 
  FROM stride5.mgrep mg, terminology3.str2tid t1 
  WHERE t1.tid in (7190, 10842)
  AND mg.tid=t1.tid group by tid;


  SELECT DISTINCT count(mg.nid), t1.tid as tid 
  FROM stride5.mgrep mg, terminology3.str2tid t1 
  WHERE t1.tid=7190
  AND mg.tid=t1.tid group by tid;

   SELECT DISTINCT count(mg.nid), t1.tid as tid 
  FROM stride5.mgrep mg, terminology3.str2tid t1 
  WHERE t1.tid in (7190)
  AND mg.tid=t1.tid group by tid;