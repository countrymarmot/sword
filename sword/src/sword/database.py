'''
Created on Sep 17, 2013

@author: mzfa
'''
import MySQLdb
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
import os


class MyDB(object):
    '''
    base MySQL DB class
    '''
    __CONFIG = './config/database.xml'
    
    __DB_ADDR = 'localhost'
    __DB_NAME = 'trackpad'
    __USER = 'test'
    __PSW = '12345678'    
    conn = None
    cur = None
    
    def __init__(self):
        '''
        Constructor
        '''
        
        if(os.path.exists(self.__CONFIG)):
            tree = ET.parse(self.__CONFIG)
            root = tree.getroot()
            self.__DB_ADDR = root.find('host').text
            self.__DB_NAME = root.find('dbname').text
            self.__USER = root.find('user').text
            self.__PSW = root.find('pass').text
            
    def conn_db(self):
        '''
        connect MySQL database
        '''
        try:
            self.conn = MySQLdb.connect(host=self.__DB_ADDR, user=self.__USER, passwd=self.__PSW , db=self.__DB_NAME, port=3306)
            self.cur = self.conn.cursor()
#             print "MySQL connected:"
        except MySQLdb.Error, e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])
            
    def disconnect(self):
        '''
        disconnect MySQL database
        '''
        try:
            self.cur.close()
            self.conn.close()
#             print "MySQL disconnected."
        except MySQLdb.Error, e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])
        
    def insert_single(self, xml_rootree):
        try:
            sn = xml_rootree.findtext('Serial_Number')[1:-1]
            pt = sn[0:8]
            ts = xml_rootree.findtext('Test_Station')[0:3]
            ec = xml_rootree.findtext('Error_Code')
            tt = xml_rootree.findtext('Test_Time')
            fv = xml_rootree.findtext('Firmware_Revision')
            idd = xml_rootree.findtext('IDD_Value')
            if (ts == 'IDD'):
                value = (sn , ts , pt , ec , idd , fv , tt , 0)
                dutid = self.__insert_dut(value)
                if dutid == -1:
                    return
                sleep1 = xml_rootree.findtext('IDD_Sleep1_Value')
                deep_sleep = xml_rootree.findtext('IDD_Deep_Sleep_Value')
                self.__insert_idd((dutid, sleep1, deep_sleep))
                self.conn.commit()
            else:
                value = (sn , ts , pt , ec , idd , fv , tt , 0)
                dutid = self.__insert_dut(value)
                if dutid == -1:
                    return
                sub_item_table = {
                    'Raw_Count_Averages': 'rawdata',
                    'Raw_Count_Noise':  'noise',
                    'Global_IDAC_Value': 'global_idac',
                    'IDAC_Value': 'global_idac'
                }
                for child_of_root in xml_rootree:
                    item = child_of_root.tag
                    if sub_item_table.has_key(item):
                        values = []
                        i = 1
                        for child in child_of_root:
                            values.append((dutid, i, child.text))
                            i = i + 1
                        self.__insert_sub(sub_item_table[item], values)
                self.conn.commit()    
        except MySQLdb.Error, e:
            self.conn.rollback()
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])
        
    def log_check(self, sn, tt):
        try:
            pt = sn[0:8]
            value = (pt, sn, tt)
            sql = "SELECT `Id` FROM dut WHERE `PartType` = %s AND `SerialNumber` = %s AND `TestTime` = %s;"
            count = self.cur.execute(sql, value)
            self.conn.commit()
            return count
        
        except MySQLdb.Error, e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])
            
    def update_status(self , sn , ts):
        try:
            pt = str(sn)[0:8]
            sql = " SELECT MAX(`TestTime`) FROM `dut` WHERE `PartType` = '" + pt + "' AND `TestStation` = '" + ts + "' AND `SerialNumber` = '" + sn + "';"
            count = self.cur.execute(sql)
            if count > 0:
                last_time = self.cur.fetchone()[0].strftime('%Y-%m-%d %H:%M:%S')
                values = (pt, ts , sn , last_time)
                sql1 = " UPDATE `dut` SET `TestStatus` = 0 WHERE `part_number` = %s AND `test_station` = %s AND `serial_number` = %s  AND `test_time` = %s"
                sql2 = " UPDATE `dut` SET `TestStatus` = 1 WHERE `part_number` = %s AND `test_station` = %s AND `serial_number` = %s  AND `test_time` < %s"
                self.cur.execute(sql1, values)
                self.cur.execute(sql2, values)
                self.conn.commit()
            else:
                return
            
        except MySQLdb.Error, e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])
    
    def __insert_dut(self, value):
        try:
            sql = "INSERT IGNORE INTO `dut`(`serial_number`,`test_station`,`part_number`,`error_code`,`icom`,`fw_revision`,`test_time`,`TestStatus`) "
            +"VALUES (%s ,%s ,%s ,%s ,%s ,%s ,%s, %s)"
            count = self.cur.execute(sql , value)
            if (int(count) <= 0):
                return -1
            else:
                dutid = self.conn.insert_id()
            return dutid
                        
        except MySQLdb.Error, e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])
            
    def __insert_idd(self, value):
        try:
            sql = "INSERT IGNORE INTO `icom` VALUES (NULL ,%s ,%s ,%s)"
            count = self.cur.execute(sql , value)
            if (int(count) <= 0):
                self.conn.rollback()
                return -1
            else:
                dutid = self.conn.insert_id()
            return dutid
                        
        except MySQLdb.Error, e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])
    
    def __insert_sub(self, table , values):
        try:
            sql = "INSERT IGNORE INTO `" + table + "` VALUES (NULL,%s,%s,%s);"
            self.cur.executemany(sql, values)
            
        except MySQLdb.Error, e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])

    
if __name__ == "__main__":
    import xmlog_parse
    xml_rootree = xmlog_parse.parse('D:\\TestLogForDev\\20130610\\TMT\\116002000313091TMT3.xml')
