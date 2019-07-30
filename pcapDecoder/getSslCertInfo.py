 # encoding: utf-8 
 #pip install pyopenssl
import json
import os
import sys
import json
import sqlite3
from OpenSSL import crypto
import gc 
import time
import multiprocessing

def getCertSubjectInfo(certName):
    
    certSubjectInfo = []
    try:
        cert = crypto.load_certificate(crypto.FILETYPE_ASN1, open(certName).read()) 
        subject = cert.get_subject() 
        certSubjectInfo.append(subject.O)
        certSubjectInfo.append(subject.C)
        certSubjectInfo.append(subject.L)
        certSubjectInfo.append(subject.ST)
        certSubjectInfo.append(subject.CN)
        certSubjectInfo.append(subject.OU)
        # 得到证书颁发机构 
        #issuer = cert.get_issuer() 
        #issued_by = issuer.CN
        #if subject.O != None:
            #print(subject.O) 
        san = None
        for index in range(cert.get_extension_count()):                                                                                                                                                         
            ext = cert.get_extension(index)                                                                                                                                                                          
            if 'subjectAltName' == ext.get_short_name():                                                                                                    
                #print(str(ext))
                san = str(ext)
                break
            else:
                pass
        certSubjectInfo.append(san)
        del cert
        del subject
        del ext
        gc.collect()
    except Exception as e:
        print(certName)
        print(e)
    return certSubjectInfo

def getAllFileName(filePath,allFileName):
    #for filename in os.listdir(filePath):
        #allFileName.append(filename)
        #print(filename)

    #allFileName.sort()

    for root,dirs,files in os.walk(filePath):
        for f in files:
            allFileName.append(os.path.join(root,f))
            #print(os.path.join(root,f).split('/')[-1])

    allFileName.sort()

def createSqlite3Table():
    conn = sqlite3.connect('pcapInfo.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS SSL_CERT_INFO
       (SNI          TEXT  NOT NULL,
       STREAM        INT,
       SRC_IP        TEXT,
       SRC_PORT      INT,
       DST_IP        TEXT,
       DST_PORT      INT,
       IP_VERSION    INT,
       CERT_O        TEXT,
       CERT_C        TEXT,
       CERT_L        TEXT,
       CERT_ST       TEXT,
       CERT_CN       TEXT,
       CERT_OU       TEXT,
       CERT_SAN      TEXT);''')

    conn.commit()
    conn.close()

def insertDataToSqlite3Table(data):

    conn = sqlite3.connect('pcapInfo.db')
    c = conn.cursor()
    insert_sql = 'INSERT INTO SSL_CERT_INFO (SNI,STREAM,SRC_IP,SRC_PORT,DST_IP,DST_PORT,IP_VERSION,CERT_O,CERT_C,CERT_L,CERT_ST,CERT_CN,CERT_OU,CERT_SAN) \
          VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)'
    #print("insertDataToSqlite3Table")

    #c.execute(insert_sql,data);
    c.executemany('INSERT INTO SSL_CERT_INFO VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)', data)
    conn.commit()
    conn.close()


def readSqlite3Table():
    conn = sqlite3.connect('pcapInfo.db')
    c = conn.cursor()
    c.execute('select * from SSL_CERT_INFO')
    #print c.fetchall()

def task(aCertFileName,rowInfo,lock):
    aFileNameInfo = aCertFileName.split('/')[-1].split('_')

    aFileNameInfo[-1] = aFileNameInfo[-1][0]#只取4.cer中的ipversion部分4
    aCertSubjectInfo = getCertSubjectInfo(aCertFileName)

    with lock:
        if (len(rowInfo) % 50000 == 0):
            print(len(rowInfo))

        if(14 == len(aFileNameInfo + aCertSubjectInfo)):
            rowInfo.append(aFileNameInfo + aCertSubjectInfo)

    #return aFileNameInfo + aCertSubjectInfo
    #print(rowInfo)

if __name__ == '__main__':

    if len (sys.argv) < 2:
        print('HELP: python {} <CERT_PATH>'.format(sys.argv[0]))
        sys.exit(0)
        #_EXIT_

    certFilePath = sys.argv[1]

    createSqlite3Table()

    allCertFileName = []
    
    #ketList = ['SNI','STREAM','SRC_IP','SRC_PORT','DST_IP','DST_PORT','IP_VERSION']

    getAllFileName(certFilePath,allCertFileName)

    #rowInfo =  multiprocessing.Array("i",[])
    manager =  multiprocessing.Manager()
    rowInfo =  manager.list()
    lock = manager.Lock()
    pool = multiprocessing.Pool(processes = 50)
    

    startTime = time.time()

    for aCertFileName in allCertFileName:
        #task(aCertFileName)
        pool.apply_async(task, args=(aCertFileName,rowInfo,lock,))

    pool.close()
    pool.join()

    endTime = time.time()

    print("多进程执行耗时：{0:.2f}".format(endTime - startTime))
    #print(rowInfo)
    insertDataToSqlite3Table(rowInfo)
    #readSqlite3Table()
    #cert_file = '/home/zte/data/erde/googleFreeTrans/unrn/code/pcapDecoder/pcapFile/Custom_00_20190704113328_0000_finish/z9.cnzz.com_1173_10.190.231.236_46342_203.119.206.97_443_4.cer'
    #cert_file = '/home/zte/data/erde/googleFreeTrans/unrn/code/pcapDecoder/pcapFile/Custom_00_20190704113328_0000_finish/59.111.21.13_1081_10.185.218.247_58655_59.111.21.13_443_4.cer'

    