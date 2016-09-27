#!/usr/bin/python
#coding:utf-8

import xml.etree.cElementTree as ET
import sys,os
from multiprocessing import Process
import logging
#import db
import psycopg2 as psycopg

def getRoot(fileName):
    return ET.parse(fileName).getroot()

def getMd5(root):
    PROC = root.find("PROC")
    if not PROC:
        return ""
    HASH = PROC.find("HASH")
    if not HASH:
        return ""

    MD5 = HASH.find("MD5")
    if MD5 is None:
        return ""

    return MD5.text

def collectTargetInfo(root,fileName):`
    item = dict()

    item["md5"] = getMd5(root)

    FINALCP = root.find("FINALCP")
    if not FINALCP:
        logging.error(fileName + "\tlost FINALCP tag")
    else:
        PACKINFO= FINALCP.find("PACKINFO")
        if PACKINFO is not None:
            item["packinfo_ispack"] = PACKINFO.attrib.get("ispack") or False
            item["packinfo_text"] = PACKINFO.text or ""
        else:
            item["packinfo_ispack"] = False
            item["packinfo_text"] = ""

        ARCHIVEINFO= FINALCP.find("ARCHIVEINFO")
        if ARCHIVEINFO is not None:
            item["archiveinfo_isarchive"] = ARCHIVEINFO.attrib.get("isarchive") or False
            item["archiveinfo_text"] = ARCHIVEINFO.text or ""
        else:
            item["archiveinfo_isarchive"] = False
            item["archiveinfo_text"] = ""


        INFECTEDJUDGEMENT= FINALCP.find("INFECTEDJUDGEMENT")
        if INFECTEDJUDGEMENT is not None:
            item["infectedjudgement"]= INFECTEDJUDGEMENT.text or False
        else:
            item["infectedjudgement"]= False

        SELFEXTRACTARCHIVE = FINALCP.find("SELFEXTRACTARCHIVE")
        if SELFEXTRACTARCHIVE is not None:
            item["selfextractarchive_flag"] = SELFEXTRACTARCHIVE.attrib.get("flag") or False
            item["selfextractarchive_text"] = SELFEXTRACTARCHIVE.text or ""
        else:
            item["selfextractarchive_flag"] = False
            item["selfextractarchive_text"] = ""

        FORMATNAME = FINALCP.find("FORMATNAME")
        if FORMATNAME is not None:
            item["formatname_flag"] = FORMATNAME.attrib.get("flag") or False
            item["formatname_text"] = FORMATNAME.text or ""
        else:
            item["formatname_flag"] = False
            item["formatname_text"] = ""

        ARCHIVEBOM = FINALCP.find("ARCHIVEBOM")
        if ARCHIVEBOM is not None:
            item["archivebom"] = ARCHIVEBOM.text or False
        else:
            item["archivebom"] = False

        ISEXEEMBEDDED = FINALCP.find("ISEXEIMBEDDED")
        if ISEXEEMBEDDED is not None:
            item["isexeembedded"] = ISEXEEMBEDDED.text or False
        else:
            item["isexeembedded"] = False

    return item

'''
def dropIntoDb(item):
    sql = "insert into  sampleInfo (md5,packinfo_ispack,\
            packinfo_from,packinfo_text,archiveinfo_isarchive,\
            archiveinfo_from,archiveinfo_text,infectedjudgement,\
            selfextractarchive_flag,selfextractarchive_text,\
            formatname_flag,formatname_text,archivebom,isexeembedded) \
            values ('%s',%s,'%s','%s',%s,'%s','%s','%s',%s,'%s',%s,'%s',%s,%s)" % (item["md5"],\
            item["packinfo_ispack"],item["packinfo_from"],item["packinfo_text"],item["archiveinfo_isarchive"],\
            item["archiveinfo_from"],item["archiveinfo_text"],item["infectedjudgement"],\
            item["selfextractarchive_flag"],item["selfextractarchive_text"],\
            item["formatname_flag"],item["formatname_text"],item["archivebom"],item["isexeembedded"])

    db.do_sql(sql)
'''

def itemCheckOk(item):
    #check item exists all values
    # log if not ok
    message = ""
    if "md5" not in item or len(item["md5"]) != 32:
        message = "  md5 check error"
        return False,message

    if "packinfo_ispack" not in item:
        message = "  packinfo_ispack check error"
        return False,message

    return True,message

def processOneFile(*args):
    conn= psycopg.connect("host=10.255.49.44 dbname=20160926 user=postgres password=sw!3OlfdUeT&VY1a7XC@xEZZ",)
    cur =conn.cursor()
    files = args[0]
    directory = args[1]

    for f in files:
        fileName = directory + f
        root = getRoot(fileName)
        item = collectTargetInfo(root, fileName)

        ok,message = itemCheckOk(item)
        if ok:
            sql = "insert into  sampleInfo (md5,packinfo_ispack,\
            packinfo_text,archiveinfo_isarchive,\
            archiveinfo_text,infectedjudgement,\
            selfextractarchive_flag,selfextractarchive_text,\
            formatname_flag,formatname_text,archivebom,isexeembedded) \
            values ('%s',%s,'%s',%s,'%s','%s',%s,'%s',%s,'%s',%s,%s)" % (item["md5"],\
            item["packinfo_ispack"],item["packinfo_text"],item["archiveinfo_isarchive"],\
            item["archiveinfo_text"],item["infectedjudgement"],\
            item["selfextractarchive_flag"],item["selfextractarchive_text"],\
            item["formatname_flag"],item["formatname_text"],item["archivebom"],item["isexeembedded"])

            cur.execute(sql)
        else:
            logging.error("file:" + fileName + message)

    cur.close()
    conn.commit()
    conn.close()


if __name__ == "__main__":
    logging.basicConfig(filename="xml.log")
    pNum = 1
    directory = "data/"
    files = os.listdir(directory)

    jobs = []
    size = len(files)/pNum
    for i in range(pNum):
        if i+1 == pNum:
            j = Process(target=processOneFile,name=str(i),args=(files[i*size:],directory))
        else:
            j = Process(target=processOneFile,name=str(i),args=(files[i*size:(i+1)*size],directory))

        jobs.append(j)
        j.start()

    for j in jobs:
        j.join()
        #print '%s.exitcode = %s' % (j.name, j.exitcode)
