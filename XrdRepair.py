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
        parser.add_option("-i", "--input", dest='filelist',default="filelist.txt",help=_('Input filelist to check'))  
        parser.add_option("-s", "--step", dest='step',default=1,help=_('Number of step to display'))
        parser.add_option("-c", "--config", dest='configFile',default="config.ini",help=_('Config file')) 
        parser.add_option("-a", "--autorecover", dest='auto',action="store_true",default=False,help=_('Auto recovery using DBS')) 
        parser.add_option("-o", "--output", dest='output',default="output.md",help=_('Set a filename for report output')) 
        parser.add_option("-v", "--verbose", dest='verbose',action='store_true',help=_('Verbose mode'))                                                       
        (options, args) = parser.parse_args()
        self.filelist = options.filelist
        self.step = options.step
        self.config = ConfigParser()
        self.config.read(options.configFile)
        self.XrdHost   = self.config['XrdRepair']['XrdHost']
        self.XrdPrefix = self.config['XrdRepair']['XrdPrefix']
        self.output = options.output
        self.verbose = options.verbose
        self.auto = options.auto
    def checkingfile(self):
        if self.verbose: 
            print(self.XrdHost, self.XrdPrefix)
        filenames = open(self.filelist).readlines()
        self.total_files = len(filenames)
        count = {'normal file':0,'duplicated file':0,'missing file':0,'broken file':0}
        check_filelist = {'duplicated file':{}, 'missing file':[], 'broken file':[] }
        for idx,fileinfo in enumerate(filenames):
            filename, size = fileinfo.split()
            if (idx % int(self.step)==0) : 
                print(f"{idx+1}/{self.total_files} : {filename}")
            myclient = client.FileSystem(f"{self.XrdHost}")
            xrd_filepath = f"{self.XrdPrefix}{filename}"
            if self.verbose: 
                print(f"xrd_filepath : {xrd_filepath}")
            status, deeplocate = myclient.deeplocate(xrd_filepath,OpenFlags.READ)
            if ( deeplocate is not None):
                if ( len(deeplocate.locations) ==1 ):
                    status, stat = myclient.stat(xrd_filepath)
                    if int(stat.size)==int(size):
                        count['normal file'] = count['normal file']+1
                    else:
                        count['broken file'] = count['broken file'] + 1
                        check_filelist['broken file'].append(filename)
                elif( len(deeplocate.locations)==0):
                    count['missing file'] = count['missing file'] + 1
                    check_filelist['missing file'].append(filename)
                elif (len(deeplocate.locations)>=2):
                    check_filelist['duplicated file'][filename] = []
                    for location in deeplocate.locations:
                        myclient2 = client.FileSystem(f"{location.address}")
                        status, stat = myclient2.stat(xrd_filepath)
                        if self.verbose:
                            print(stat)
                        if int(stat.size)==int(size):
                            check_filelist['duplicated file'][filename].append((location.address,"OK",stat.size))
                        else:
                            check_filelist['duplicated file'][filename].append((location.address,"Failed",stat.size))
                    count['duplicated file'] = count['duplicated file'] + 1
                else: 
                    print(_("Unknown error!"))
                    print( deeplocate)
            else:
                print(_("No response about filename"))
                print(status)
        self.count = count
        self.checklist = check_filelist
    def report(self):
        if self.verbose:
            print(self.count)
            print(self.checklist)

        with open(self.output,'w') as mdfile:
            mdfile.write(_("# File Scan Report on the XRootD System\n"))
            mdfile.write(_("## Scan configuration\n"))
            mdfile.write(_(f"* Repair mode : {self.auto}\n"))
            mdfile.write(_(f"## Total Number of files: {self.total_files}\n"))
            mdfile.write(_(f"* Number of Normal files: {self.count['normal file']}\n"))
            mdfile.write(_(f"* Number of Duplicated files: {self.count['duplicated file']}\n"))
            for duplicated_file in self.checklist['duplicated file'].keys():
                mdfile.write(f"   * {duplicated_file}\n")
                for (address, status, size) in self.checklist['duplicated file'][duplicated_file]:
                    mdfile.write(f"      * ```{address}```\n")
                    mdfile.write(f"         * Status is {status}\n")
                    mdfile.write(f"         * Size is {size}\n")
            mdfile.write(_(f"* Number of Missing  files: {self.count['missing file']}\n"))
            for missing_file in self.checklist['missing file']:
                mdfile.write(f"   * {missing_file}\n")
            mdfile.write(_(f"* Number of broken  files: {self.count['broken file']}\n"))
            for broken_file in self.checklist['broken file']:
                mdfile.write(f"   * {broken_file}\n")


if __name__ == "__main__":
    xr = XrdRepair()
    xr.checkingfile()
    xr.report()
