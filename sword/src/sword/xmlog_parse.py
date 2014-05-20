'''
Created on Sep 18, 2013

@author: mzfa
'''
import re
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
    
def parse(singlefile):
    parsedata = ParseData()
    parsedata.cleanup_xml(singlefile)
    tree = parsedata.parse_one_file(singlefile)
    root = tree.getroot()
    return root
    
class ParseData(object):
    
    def cleanup_xml(self, singlefile):
        '''
        clean up the "Signal Value" to "signal_value" ;
        celan up the "D" to "data";
        '''
        clean_file = CleanupXML()

        clean_file.change_D_to_data(singlefile)
        clean_file.change_signal_tag(singlefile)
        clean_file.change_serialnumber_to_string(singlefile)
        clean_file.change_time_format(singlefile)
    
    def parse_one_file(self, singlefile):
        try:
            tree = ET.parse(singlefile)
            return tree
            
        except Exception, e:
            print singlefile + " get_data: " + str(e)
            return 0
    

class CleanupXML(object):

    def change_D_to_data(self, file_path):
        '''
        change xml tag "D" to "data"
        '''
        # open singlefile for read and write
        log_file = open(file_path, "r+")
        log_string = log_file.read()

        regex_m = re.compile(r"<D\d+>")
        log_string = regex_m.sub('<data>', log_string)

        regex_n = re.compile(r"</D\d+>")
        log_string = regex_n.sub('</data>', log_string)

        log_file.seek(0)  # point to the head of singlefile
        log_file.write(log_string)  # write the string
        log_file.close()

    def change_serialnumber_to_string(self, file_path):
        log_file = open(file_path, "r")  # open file for read
        log_string = log_file.read()

        regex = re.compile(
            r"<Serial_Number>(?P<SerialNumber>\w{19})</Serial_Number>")
        r = regex.search(log_string)

        log_file.close()

        if r is not None:
            # group(0) is the whole match, from <Serial_number>.
            # group(1) is the second match, the \w{19}.
            serialnumber = "<Serial_Number>'" + \
                r.group(1) + \
                "'</Serial_Number>"
            # replace with the ' '
            log_string = regex.sub(serialnumber, log_string)

            log_file = open(file_path, "w")  # open file for write
            log_file.truncate()
            log_file.seek(0)  # point to the head of file
            log_file.write(log_string)  # write the string

    def change_time_format(self, file_path):
        log_file = open(file_path, "r")  # open the read of file
        log_string = log_file.read()

        regex = re.compile(r"<Test_Time>(?P<TestTime>.{20})</Test_Time>")
        r = regex.search(log_string)

        log_file.close()  # close the read of file

        if r is not None:
            # cut the last Z
            testtime = "<Test_Time>" + r.group(1)[:-1] + "</Test_Time>"
            log_string = regex.sub(testtime, log_string)

            log_file = open(file_path, "w")  # open the write of file
            log_file.truncate()
            log_file.seek(0)  # point to the head of file
            log_file.write(log_string)  # write the string

    def change_signal_tag(self, file_path):
        '''
        change xml tag "Signal Value" to "signal_value"
        '''
        log_file = open(file_path, "r+")
        log_string = log_file.read()

        regex_m = re.compile(r"<Signal\sValue>")
        log_string = regex_m.sub("<signal_value>", log_string)

        regex_n = re.compile(r"</Signal\sValue>")
        log_string = regex_n.sub("</signal_value>", log_string)

        log_file.seek(0)
        log_file.write(log_string)
        log_file.close()
        
        
if __name__ == "__main__":
    parse('D:\\TestLogForDev\\20130610\\TMT\\116002000313091TMT3.xml')
