'''
Created on Sep 25, 2013

@author: mzfa
'''
import re

SN_PATTERN = re.compile(r'^[01][01]\d{1}0\d{1}\d{1}000[1-9]([0][1-9]|[1][0-5])([0-4]\d{1}|5[0-3])[0-6][a-zA-Z0-9][a-zA-Z0-9][a-zA-Z0-9][1-8]$')
TS_PATTERN = re.compile(r'^TMT|TPT|IDD StandBy$')
EC_PATTERN = re.compile(r'^\d+')
TT_PATTERN = re.compile(r'^20[01]\d{1}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01]) ([01]\d|2[0-3])(:[0-5]\d)(:[0-5]\d)$')

def log_is_valid(xml_rootree):
    sn = xml_rootree.findtext('Serial_Number')[1:-1]
    ts = xml_rootree.findtext('Test_Station')
    ec = str(xml_rootree.findtext('Error_Code'))
    tt = xml_rootree.findtext('Test_Time')
    if not SN_PATTERN.search(sn):
        print '\'Serial Number\'',
        return False
    if not TS_PATTERN.search(ts):
        print '\'Test Station\'',
        return False
    if not EC_PATTERN.search(ec):
        print '\'Error Code\'',
        return False
    if not TT_PATTERN.search(tt):
        print '\'Test Time\'',
        return False
    return True
