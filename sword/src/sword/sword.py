'''
Created on Sep 18, 2013

@author: mzfa
'''

import sys
import files
import xmlog_parse
import database
import verify_log
import shutil
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
    
    
def run():
    __CFG = './config/g3_cfg.xml'
    
    if len(sys.argv) < 2:
        print "add \'CM NAME\' and \'NUMBER OF FOLDER(optional)\' ARGs to handle after"
        sys.exit()
    elif len(sys.argv) > 3:
        print "too much params, only CM and folder number needed"
        sys.exit()
    else:
        folders = []
        i = 1
        cm_name = sys.argv[1]
        f_num = 10000
        if len(sys.argv) == 3:
            f_num = int(sys.argv[2])
        config = ET.parse(__CFG)
        root = config.getroot()
        log_folders = root.find(".//CM[@name='" + cm_name + "']/log_folders")
        invalid_folder = root.find(".//CM[@name='" + cm_name + "']/invalid_logs").text
        mydb = database.MyDB()
        mydb.conn_db()
        for fl in log_folders:
            folders.append(fl.text)
        for folder in folders:
            for f in files.get_xml_files(folder, f_num):
                xml_root_tree = xmlog_parse.parse(f)
                print i,
                if verify_log.log_is_valid(xml_root_tree):
                    insert_one_log(xml_root_tree, mydb)
                else:
                    shutil.copy(f, invalid_folder)
                    print "is invalid in file:", f
                i = i + 1
        mydb.disconnect()
        
def insert_one_log(xml_rootree, mydb):
    try:
        sn = xml_rootree.findtext('Serial_Number')[1:-1]
        ts = xml_rootree.findtext('Test_Station')[0:3]
        tt = xml_rootree.findtext('Test_Time')
        count = mydb.log_check(sn, tt)
        if (count != 0):
            print sn, ts, tt, "EXISTED!!"
        else:
            mydb.insert_single(xml_rootree)
            mydb.update_status(sn, ts)
            print sn, ts, tt, "inserted"
            
    except database.MySQLdb.Error, e:
        print "Mysql Error %d: %s" % (e.args[0], e.args[1])
        mydb.mydb.conn.rollback()

if __name__ == "__main__":
    run()
