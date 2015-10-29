#!/usr/bin/env python

# $Id$
# $Rev::                                  $:  # Revision of last commit.
# $LastChangedBy::                        $:  # Author of last commit.
# $LastChangedDate::                      $:  # Date of last commit.

# RAG add imports

import pyfits 

def fwhmFromFITS_LDAC(incat,debug):
    """
    Get the median FWHM and ELLIPTICITY from the scamp (FITS_LDAC) catalog (incat)
    """

    CLASSLIM = 0.75      # class threshold to define star
    MAGERRLIMIT = 0.1  # mag error threshold for stars

    if debug: print("(fwhmFromFITS_LDAC) Opening scamp_cat ({:s}) to calculate median FWHM & ELLIPTICITY.".format(incat))
    hdu = pyfits.open(incat,"readonly")

    if debug: print("(fwhmFromFITS_LDAC) Checking to see that hdu2 in scamp_cat is a binary table.")
    if 'XTENSION' in hdu[2].header:
        if hdu[2].header['XTENSION'] != 'BINTABLE':
            print("Error: (fwhmFromFITS_LDAC): this HDU is not a binary table")
            exit(1)
    else:
        print("(fwhmFromFITS_LDAC) XTENSION keyword not found")
        exit(1)

    if 'NAXIS2' in hdu[2].header:
        nrows = hdu[2].header['NAXIS2']
        print "(fwhmFromFITS_LDAC) Found %s rows in table" % nrows
    else:
        print("Error: (fwhmFromFITS_LDAC) NAXIS2 keyword not found")
        exit(1)

    tbldct = {}
    for colname in ['FWHM_IMAGE','ELLIPTICITY','FLAGS','IMAFLAGS_ISO','MAGERR_AUTO','CLASS_STAR']:
        if colname in hdu[2].columns.names:
            tbldct[colname] = hdu[2].data.field(colname)
        else:
            if (colname in ['IMAFLAGS_ISO']):
                print "(fwhmFromFITS_LDAC): Optional column %s not present in binary table" % colname
            else:
                print "(fwhmFromFITS_LDAC): Required column %s not present in binary table" % colname
                exit(1)

    hdu.close()

    flags = tbldct['FLAGS']
    cstar = tbldct['CLASS_STAR']
    mgerr = tbldct['MAGERR_AUTO']
    fwhm = tbldct['FWHM_IMAGE']
    ellp = tbldct['ELLIPTICITY']

    fwhm_sel = []
    ellp_sel = []
    count = 0
    for i in range(nrows):
        if flags[i] < 1 and cstar[i] > CLASSLIM and mgerr[i] < MAGERRLIMIT and fwhm[i]>0.5 and ellp[i]>=0.0:
            fwhm_sel.append(fwhm[i])
            ellp_sel.append(ellp[i])
            count+=1

    fwhm_sel.sort()
    ellp_sel.sort()

    # allow the no-stars case count = 0 to proceed without crashing
    if count <= 0:
      fwhm_med = 4.0
      ellp_med = 0.0
    else:
      if count%2:
        # Odd number of elements
        fwhm_med = fwhm_sel[count/2]
        ellp_med = ellp_sel[count/2]
      else:
        # Even number of elements
        fwhm_med = 0.5 * (fwhm_sel[count/2]+fwhm_sel[count/2-1])
        ellp_med = 0.5 * (ellp_sel[count/2]+ellp_sel[count/2-1])

    if debug:
        print "(fwhmFromFITS_LDAC):     FWHM=%.4f " % (fwhm_med)
        print "(fwhmFromFITS_LDAC): ELLIPTIC=%.4f " % (ellp_med)
        print "(fwhmFromFITS_LDAC): NFWHMCNT=%s " % (count)

    return (fwhm_med,ellp_med,count)

