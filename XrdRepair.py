#!/usr/bin/env python3
from XRootD import client
from XRootD.client.flags import DirListFlags, OpenFlags, MkDirFlags, QueryCode
from optparse import OptionParser
from configparser import ConfigParser

#from babel import Locale
import gettext
t = gettext.translation('messages','locale',fallback=True)
_ = t.gettext

class XrdRepair:
    def __init__(self):
        ## Parse Option and Config                                                                                                                             
        parser = OptionParser(usage=_('Usage: %prog [options]'))
        parser.add_option("-i", "--input", dest='filelist',default="filelist.txt",help=_('input filelist to check'))  
        parser.add_option("-s", "--step", dest='step',default=1,help=_('Number of step to display'))
        parser.add_option("-c", "--config", dest='configFile',default="config.ini",help=_('Config file')) 
        parser.add_option("-a", "--autorecover", dest='auto',action="store_true",default=False,help=_('Auto recovery using DBS')) 
        parser.add_option("-v", "--verbose", dest='verbose',action='store_true',help=_('Verbose mode'))                                                       
        (options, args) = parser.parse_args()
        self.filelist = options.filelist
        self.step = options.step
        self.config = ConfigParser()
        self.config.read(options.configFile)
        self.XrdHost   = self.config['XrdRepair']['XrdHost']
        self.XrdPrefix = self.config['XrdRepair']['XrdPrefix']
        self.verbose = options.verbose
    def checkingfile(self):
        if self.verbose: 
            print(self.XrdHost, self.XrdPrefix)
        filenames = open(self.filelist).readlines()
        count = {'normal':0,'duplicated':0,'nofile':0,'wrong_size':0}
        check_filelist = {'duplicated':[], 'nofile':[], 'wrong_size':[] }
        total_files = len(filenames)
        for idx,fileinfo in enumerate(filenames):
            filename, size = fileinfo.split()
            if (idx % int(self.step)==0) : 
                print(f"{idx+1}/{total_files} : {filename}")
            myclient = client.FileSystem(f"{self.XrdHost}")
            xrd_filepath = f"{self.XrdPrefix}{filename}"
            if self.verbose: 
                print(f"xrd_filepath : {xrd_filepath}")
            status, deeplocate = myclient.deeplocate(xrd_filepath,OpenFlags.READ)
            if ( deeplocate is not None):
                if ( len(deeplocate.locations) ==1 ):
                    status, stat = myclient.stat(xrd_filepath)
                    if int(stat.size)==int(size):
                        count['normal'] = count['normal']+1
                    else:
                        count['wrong_size'] = count['wrong_size'] + 1
                        check_filelist['wrong_size'].append(filename)
                elif( len(deeplocate.locations)==0):
                    count['nofile'] = count['nofile'] + 1
                    check_filelist['nofile'].append(filename)
                elif (len(deeplocate.locations)>=2):
                    for location in deeplocate.locations:
                        myclient2 = client.FileSystem(f"{location.address}")
                        status, stat = myclient2.stat(xrd_filepath)
                        if self.verbose:
                            print(stat)
                        if int(stat.size)==int(size):
                            count['duplicated'] = count['duplicated']+1
                            check_filelist['duplicated'].append(filename)
                        else:
                            count['wrong_size'] = count['wrong_size'] + 1
                            check_filelist['wrong_size'].append(filename)

                    check_filelist['duplicated'].append(filename)
                else: 
                    print(_("Unknown error!"))
                    print( deeplocate)
            else:
                print(_("No response about filename"))
                print(status)
        self.count = count
        self.checklist = check_filelist
    def report(self):
        print(self.count)
        print(self.checklist)


if __name__ == "__main__":
    xr = XrdRepair()
    xr.checkingfile()
    xr.report()
