#!/usr/bin/env python

# $Id: split_head.py 40435 2015-10-19 20:26:15Z mgower $
# $Rev::                                  $:  # Revision of last commit.
# $LastChangedBy:: mgower                 $:  # Author of last commit.
# $LastChangedDate:: 2015-10-19 15:26:15 #$:  # Date of last commit.

import argparse
import shutil
import unicodedata
import stat
import math
import os
import re
import csv
import sys

import pyfits
import numpy

from despyastro.fwhmFromFITS_LDAC import fwhmFromFITS_LDAC
from despyastro.CCD_corners import CCD_corners
from databaseapps.xmlslurp import Xmlslurper

####################################

if __name__ == "__main__":
    """ 
    Utility to obtain WCS header update information from SCAMP .head file and 
    update a FITS file with the appropriate keywords.  Optional arguments exist
    to 1) obtain QA information from the SCAMP XML output and
       2) FWHM information based on the SCAMP input catalog
    """

    svnid="$Id: UpdateScampHead.py 39583 2015-08-06 20:26:05Z rgruendl $"
    svnrev=svnid.split(" ")[2]

    parser = argparse.ArgumentParser(description='Update FITS header based on new WCS solution from SCAMP')
    parser.add_argument('-i', '--input',   action='store', type=str, default=None, help='Input Image (to be updated)')
    parser.add_argument('-o', '--output',  action='store', type=str, default=None, help='Output Image (updated image)')
    parser.add_argument('--headfile',      action='store', type=str, default=None, help='Headfile (containing most update information)')
    parser.add_argument('--hdupcfg',       action='store', type=str, default=None, help='Configuration file for header update')
    parser.add_argument('-f', '--fwhm',    action='store', type=str, default=None, help='update FWHM (argument is a FITS_LDAC catalog to be used to determine the FWHM)')
    parser.add_argument('--xml',            action='store', type=str, default=None, help='obtain limited QA info from SCAMP XML output (optional)')
    parser.add_argument('--debug',         action='store_true', default=False, help='Full debug information to stdout')
    parser.add_argument('-v','--verbose',  action='store_true', default=False, help='Flag to produce more verbose output')

    args = parser.parse_args()
    if (args.verbose):
        print "Running %s " % svnid
        print "##### Initial arguments #####"
        print "Args: ",args
#
#   Check manditory arguments
#
    if ((args.input is None)or(args.output is None)or(args.headfile is None)or(args.hdupcfg is None)):
        print("Missing mandatory argument(s)")
        if (args.input is None): print "  --input"
        if (args.output is None): print "  --output"
        if (args.headfile is None): print "  --headfile"
        if (args.hdupcfg is None): print " --hdupcfg"
        exit(1)

#
#   If args.fwhm then attempt to populate FWHM, ELLIPTIC, NFWHMCNT keywords 
#
    tmpdict = {}
    if (args.fwhm is None):
        if args.verbose: 
            print "FWHM option keyword will not be populated\n"
    else:
        if args.verbose:
            print "(UpdateScampHead): Will determine median FWHM & ELLIPTICITY and number of candidates"
        (fwhm_med,ellp_med,count)=fwhmFromFITS_LDAC(args.fwhm,debug=args.debug)
        if ((args.verbose)and(not(args.debug))):
            print " FWHM=%.4f" % fwhm_med   
            print " ELLIPTIC=%.4f" % ellp_med   
            print " NFWHMCNT=%s" % count

        tmpdict['FWHM']     = [round(fwhm_med,4),'Median FWHM from SCAMP input catalog [pixels]']   
        tmpdict['ELLIPTIC'] = [round(ellp_med,4),'Median Ellipticity from SCAMP input catalog']   
        tmpdict['NFWHMCNT'] = [count,'Number of objects used to find FWHM']

#    
#   If args.xml is present then try to "slurp" the SCAMP XML output for some additional quantities.  
#    

    if (args.xml is not None):
        if (args.verbose): 
            print("Reading SCAMP XML file: {:s}".format(args.xml))
        try:
            tmp_xml_tbl=Xmlslurper(args.xml,['FGroups']).gettables()
#
#           Possible that should redefine the keys using the same unicodedata.normalize method as for the values below
#
        except:
            print "Error: failed to slurp the data."
            pass 
        if ('FGroups' in tmp_xml_tbl):
            if (args.debug): 
                for key in tmp_xml_tbl['FGroups']:
                    print "  %s = %s" % (key,tmp_xml_tbl['FGroups'][key])
#
#           The keys we might be looking for (basically the translation between XML field names and FITS header keywords).
#
            key_pairs={}
            key_pairs['SCAMPCHI']={'fld':'astromchi2_reference_highsn','type':'float','comment':'Chi2 value from SCAMP'}
            key_pairs['SCAMPNUM']={'fld':'astromndets_reference_highsn','type':'int','comment':'Number of matched stars from SCAMP'}
#            key_pairs['SCAMPFLG']={'fld':'astromndets_reference_highsn','type':'int','comment':'Number of matched stars from SCAMP'}
            key_pairs['SCAMPREF']={'fld':'astref_catalog','type':'str','comment':'Astrometric Reference Catalog used by SCAMP'}
#
#           Check for presence of each key.  If exists then try to parse based on type expected
#
            for key in key_pairs:
                if (key_pairs[key]['fld'] in tmp_xml_tbl['FGroups']):
                    if (key_pairs[key]['type'] == "str"):
                        keyval=unicodedata.normalize('NFKD',tmp_xml_tbl['FGroups'][key_pairs[key]['fld']]).encode('ascii','ignore')
                        tmpdict[key]=[keyval,key_pairs[key]['comment']]
                    elif (key_pairs[key]['type'] == 'float'):
                        try:
                            keyval=float(tmp_xml_tbl['FGroups'][key_pairs[key]['fld']])
                            tmpdict[key]=[keyval,key_pairs[key]['comment']]
                        except:
                            try:
                                keyval=float(unicodedata.normalize('NFKD',tmp_xml_tbl['FGroups'][key_pairs[key]['fld']]).encode('ascii','ignore'))
                                tmpdict[key]=[keyval,key_pairs[key]['comment']]
                            except:
                                print 'Failed to parse value for %s = %s as float (skipping)' % ( key_pairs[key]['fld'], mp_xml_tbl['FGroups'][key_pairs[key]['fld']])
                                pass
                    elif (key_pairs[key]['type'] == 'int'):
                        try:
                            keyval=int(tmp_xml_tbl['FGroups'][key_pairs[key]['fld']])
                            tmpdict[key]=[keyval,key_pairs[key]['comment']]
                        except:
                            try:
                                keyval=int(unicodedata.normalize('NFKD',tmp_xml_tbl['FGroups'][key_pairs[key]['fld']]).encode('ascii','ignore'))
                                tmpdict[key]=[keyval,key_pairs[key]['comment']]
                            except:
                                print 'Failed to parse value for %s = %s as int (skipping)' % (key_pairs[key]['fld'], mp_xml_tbl['FGroups'][key_pairs[key]['fld']])
                                pass
                    else:
                        print('Unspecified value type for XML parsing of keywords (skipping)')

#
#   Put the FWHM and/or XML parameters into a keywords section
#
    kywds_data = tmpdict

#
#   Reading the header update configuration file.
#
    if (not(os.path.isfile(args.hdupcfg))):
        print('Header update config file (%s) not found! ',args.hdupcfg)
        exit(1)
    
    kywds_spec = {}
    if (args.verbose): print("Reading header update configuration file: {:s}".format(args.hdupcfg))
    f_hdupcfg = open(args.hdupcfg,"r")
    for line in f_hdupcfg:
        line=line.strip()
        columns=line.split(';')
        if (line[0:1] != "#"):
            FieldName=columns[0]
            kywds_spec[FieldName] = {}
            kywds_spec[FieldName]['key']=columns[1].strip()
            kywds_spec[FieldName]['type']=columns[2].strip()
            kywds_spec[FieldName]['comment']=columns[3].strip()
            kywds_spec[FieldName]['hdulist']=[]
            tmp_hdu_list=columns[4].strip().split(",")
            for item in tmp_hdu_list:
                try:
                    tmp_int=int(item)
                    kywds_spec[FieldName]['hdulist'].append(tmp_int)
                except:
                    kywds_spec[FieldName]['hdulist'].append(item)
                    pass
    f_hdupcfg.close()
#
    if (args.debug):
        for FieldName in kywds_spec:
            tmp_spec=kywds_spec[FieldName]
            print "     kywds_spec[%s] --> (%s = (type=%s) (comment=%s) (hdus=%s)" % (FieldName,tmp_spec['key'],tmp_spec['type'],tmp_spec['comment'],tmp_spec['hdulist'])
        print ""

#
#   Reading the .head file.
#
    tmpdict = {}
    if (args.verbose): print("Reading SCAMP .head file: {:s}".format(args.headfile))
    finhead = open(args.headfile,'r')
    for line in finhead:
        if re.match("^HISTORY.*",line): continue
        if re.match("^COMMENT.*",line): continue
        if re.match("^END.*",line):
            finhead.close()
            break
        # - split line into keyword and list containing value and comment
        tmplst1 = line[:-1].split('=',1)
        # - now split list into value and comment
        tmplst2 = tmplst1[1].split('/',1)
        # - strip off leading and trailing white spaces and create dictionary
        tmplst = []
        tmpstr = re.sub("\s+$","",re.sub("^\s+","",tmplst2[0]))
        tmpstr = re.sub("\s*'$","",re.sub("^'\s*","",tmpstr)) # strip out quotes and white spaces in strings
        tmplst.append(tmpstr)
        tmplst.append(re.sub("\s+$","",re.sub("^\s+",'',tmplst2[1])))
        key = re.sub("\s+$",'',re.sub("^\s+",'',tmplst1[0]))
        tmpdict[key] = tmplst
    finhead.close()

#
#   If PV1_3 and PV2_3 are not defined then add with value of 0
#
    if ('PV1_3' not in tmpdict):
        tmpdict['PV1_3']=[0.0,'Projection distortion parameter']
    if ('PV2_3' not in tmpdict):
        tmpdict['PV2_3']=[0.0,'Projection distortion parameter']
#
#   Calculate coordinates for ccd center and corners.
#
    if (args.verbose): print("Using new WCS to compute coordinates for CCD center and corners")
    # Get NAXIS1, NAXIS2 from the parent image and update temp dictionary tmpdict
    infit_header = pyfits.getheader(args.input,ext=0) # Assumes ext=0 for uncompress science image
    tmpdict['NAXIS1'] = infit_header['NAXIS1']
    tmpdict['NAXIS2'] = infit_header['NAXIS2']

    # Compute and Add RA,DEC High Low values to the key/val dictionary
    (ra0,dec0,rac1,decc1,rac2,decc2,rac3,decc3,rac4,decc4) = escorners(tmpdict)
    tmpdict['RA_CENT']  = [ra0,'RA center']
    tmpdict['DEC_CENT'] = [dec0,'DEC center']
    tmpdict['RAC1']     = [rac1,'RA corner 1']
    tmpdict['DECC1']    = [decc1,'DEC corner 1']
    tmpdict['RAC2']     = [rac2,'RA corner 2']
    tmpdict['DECC2']    = [decc2,'DEC corner 2']
    tmpdict['RAC3']     = [rac3,'RA corner 3']
    tmpdict['DECC3']    = [decc3,'DEC corner 3']
    tmpdict['RAC4']     = [rac4,'RA corner 4']
    tmpdict['DECC4']    = [decc4,'DEC corner 4']
#
#   Provisional functionality for Felipe's COADD queries
#   Not yet supported in DB.
#
    ras =numpy.array([rac1,rac2,rac3,rac4])
    decs=numpy.array([decc1,decc2,decc3,decc4])
    racmin=ras.min()
    racmax=ras.max()
    if ((racmax-racmin)>180.):
        tmpdict['CROSSRA0']=['Y','Does Image Span RA 0h (Y/N)']
        # Currently we substract 360.  Perhaps switch order instead?
        tmpdict['RACMIN']=[(ras.max()-360.0),'Minimum extent of image in RA']
        tmpdict['RACMAX']=[ras.min(),'Maximum extent of image in RA']
    else:
        tmpdict['CROSSRA0']=['N','Does Image Span RA 0h (Y/N)']
        tmpdict['RACMIN']=[ras.min(),'Minimum extent of image in RA']
        tmpdict['RACMAX']=[ras.max(),'Maximum extent of image in RA']
    tmpdict['DECCMIN']=[decs.min(),'Minimum extent of image in Declination']
    tmpdict['DECCMAX']=[decs.max(),'Maximum extent of image in Declination']
   
    if (args.verbose): 
        print(" RA_CEN,DEC_CEN = {:12.7f},{:12.7f} ".format(tmpdict['RA_CENT'][0],tmpdict['DEC_CENT'][0]))
        print("     RAC1,DECC1 = {:12.7f},{:12.7f} ".format(tmpdict['RAC1'][0],tmpdict['DECC1'][0]))
        print("     RAC2,DECC2 = {:12.7f},{:12.7f} ".format(tmpdict['RAC2'][0],tmpdict['DECC2'][0]))
        print("     RAC3,DECC3 = {:12.7f},{:12.7f} ".format(tmpdict['RAC3'][0],tmpdict['DECC3'][0]))
        print("     RAC4,DECC4 = {:12.7f},{:12.7f} ".format(tmpdict['RAC4'][0],tmpdict['DECC4'][0]))
        print("       CROSSRA0 = {:s} ".format(tmpdict['CROSSRA0'][0]))

    for key in tmpdict:
        kywds_data[key]=tmpdict[key]

    if (args.debug):
        print "(UpdateScampHead): Dict with data from .head files:"
        for keyword in kywds_data:
            print "     kywds_data[%s] = %s" % (keyword,kywds_data[keyword])
        print ""

#
#   Merge spec and data into dictionary where keys correspond to keywords and each key points
#   to a list where the first member is the keyword value and the second member is the comment
#
    if (args.verbose):
        print "(UpdateScampHead): Merging spec and data into another dictionary."

    kywds_dct = {}
    for keyword in kywds_data:
        for FieldName in kywds_spec:
            if (kywds_spec[FieldName]['key'] == keyword):
                tmplst = [None,None]
                valtype = kywds_spec[FieldName]['type']
                comment = kywds_spec[FieldName]['comment']
                val = kywds_data[keyword][0]
                if valtype == 'str':
                    tmplst[0] = val
                    tmplst[1] = comment
                elif valtype == 'int' or valtype == 'float':
                    # ... check to see if this is a number
                    try:
                        fval = float(val)
                        if valtype == 'int':
                            tmplst[0] = int(str(round(fval,0)).replace('.0',''))
                        else:
                            tmplst[0] = fval
                        tmplst[1] = comment
                    except ValueError:
                        print "Keyword (%s) value specified as int or float but data provided (%s) not a number. (skipping)" % (keyword,val)
                        pass
                else:
                    print "Unknown type (%s) specified in keywords section of input config file, (skipping)." % (valtype)
                if ((tmplst[0] is None)or(tmplst[1] is None)):
                    print "Warning: unable to process keyword (%s). Skipping." % (keyword)
                else:    
                    for hdu in kywds_spec[FieldName]['hdulist']:
                        if (hdu not in kywds_dct):
                            kywds_dct[hdu]={}
                        kywds_dct[hdu][keyword]=tmplst

    if (args.debug):
        print "(UpdateScampHead): Dict with merged keyword specs and data:"
        for hduname in kywds_dct:
            print "For HDU specfied as %s " % hduname
            for key in kywds_dct[hduname]:
                print "     kywds_dct[%s][%s] = %s" % (hduname,key,kywds_dct[hduname][key])
        print ""

#
#   Make a copy of the input file in preparation for update 
#
    if (args.verbose): 
        print "(UpdateScampHead): Making copy of detrended fits file before updating headers with scamp results."
    try:
        shutil.copy(args.input,args.output) # exception is raised if src and dst are identical
    except Exception, e:
        print "(UpdateScampHead): %s --> \"%s\"" % (e.__class__.__name__,str(e))
        exit(1)

#
#    Update header keywords in args.output:
#    HDUs that receive the update are in "kywds_hdus".  
#    Keywords and associated values and  comments are all specified in kywds_dct.  
#
    if (args.verbose): 
        print "(UpdateScampHead): Updating headers of copy with scamp results --> %s " % args.output
    hdulist = pyfits.open(args.output,mode='update')

    for hdu in kywds_dct:
        if (args.debug): 
            print "(UpdateScampHead): Updating keywords in hdu[%s]:" % hdu
        hdr = hdulist[hdu].header
        for key in sorted(kywds_dct[hdu].iterkeys()):
            if (args.debug): 
                print "   %s = %s / %s" % (key,kywds_dct[hdu][key][0],kywds_dct[hdu][key][1])
                hdr[key]=(kywds_dct[hdu][key][0],kywds_dct[hdu][key][1])
    if (args.verbose): 
        print "(UpdateScampHead): Closing/Saving image --> %s" % hdulist.filename()
    hdulist.close()


    exit(0)

