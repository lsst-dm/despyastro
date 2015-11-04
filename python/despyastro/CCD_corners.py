#!/usr/bin/env python

# $Id$
# $Rev::                                  $:  # Revision of last commit.
# $LastChangedBy::                        $:  # Author of last commit.
# $LastChangedDate::                      $:  # Date of last commit.

from despyastro import wcsutil

def DECam_corners(indict):

   #  DESDM CCD Image Corner Coordinates definitions for DECam
   #  see: https://desdb.cosmology.illinois.edu/confluence/display/PUB/CCD+Image+Corners+Coordinates
   #
   #
   #                     x-axis 
   #      (RA4,DEC4)                   (RA3,DEC3)
   #      Corner 4 +-----------------+ Corner 3
   #    (1,NAXIS2) |                 | (NAXIS1,NAXIS2)
   #               |                 |
   #               |                 |             
   #               |                 |             
   #               |                 |             
   #               |                 |             
   #               |                 |             
   #               |                 |             
   #               |                 |   y-axis
   #               |                 |             
   #               |                 |             
   #               |                 |             
   #               |                 |             
   #               |                 |
   #               |                 |
   #     (RA1,DEC1)|                 | (RA2,DEC2)            
   #      Corner 1 +-----------------+ Corner 2
   #         (1,1)                     (NAXIS1,1)

   hdr = {}
   hdr['crval1'] = float(indict['CRVAL1'][0])
   hdr['crval2'] = float(indict['CRVAL2'][0])
   hdr['crpix1'] = float(indict['CRPIX1'][0])
   hdr['crpix2'] = float(indict['CRPIX2'][0])
   hdr['ctype1'] = indict['CTYPE1'][0]
   hdr['ctype2'] = indict['CTYPE2'][0]

   # Real dictionary, no need to index to [0]
   hdr['naxis1'] = float(indict['NAXIS1'])
   hdr['naxis2'] = float(indict['NAXIS2'])

   hdr['cd1_1'] = float(indict['CD1_1'][0])
   hdr['cd1_2'] = float(indict['CD1_2'][0])
   hdr['cd2_1'] = float(indict['CD2_1'][0])
   hdr['cd2_2'] = float(indict['CD2_2'][0])

   hdr['pv1_0'] = float(indict['PV1_0'][0])
   hdr['pv1_1'] = float(indict['PV1_1'][0])
   hdr['pv1_2'] = float(indict['PV1_2'][0])
   hdr['pv1_3'] = float(indict['PV1_3'][0])
   hdr['pv1_4'] = float(indict['PV1_4'][0])
   hdr['pv1_5'] = float(indict['PV1_5'][0])
   hdr['pv1_6'] = float(indict['PV1_6'][0])
   hdr['pv1_7'] = float(indict['PV1_7'][0])
   hdr['pv1_8'] = float(indict['PV1_8'][0])
   hdr['pv1_9'] = float(indict['PV1_9'][0])
   hdr['pv1_10'] = float(indict['PV1_10'][0])

   hdr['pv2_0'] = float(indict['PV2_0'][0])
   hdr['pv2_1'] = float(indict['PV2_1'][0])
   hdr['pv2_2'] = float(indict['PV2_2'][0])
   hdr['pv2_3'] = float(indict['PV2_3'][0])
   hdr['pv2_4'] = float(indict['PV2_4'][0])
   hdr['pv2_5'] = float(indict['PV2_5'][0])
   hdr['pv2_6'] = float(indict['PV2_6'][0])
   hdr['pv2_7'] = float(indict['PV2_7'][0])
   hdr['pv2_8'] = float(indict['PV2_8'][0])
   hdr['pv2_9'] = float(indict['PV2_9'][0])
   hdr['pv2_10'] = float(indict['PV2_10'][0])

   # Short cut for less typing
   nx = hdr['naxis1']
   ny = hdr['naxis2']
   
   wcs = wcsutil.WCS(hdr)
   rac1,decc1 = wcs.image2sky(1, 1)
   rac2,decc2 = wcs.image2sky(nx,1)
   rac3,decc3 = wcs.image2sky(nx,ny)
   rac4,decc4 = wcs.image2sky(1, ny)
   ra0 ,dec0  = wcs.image2sky(nx/2.0, ny/2.0)

   # What is this!!!!?????? -- Felipe asks
   #if (rac1 > 350.0 and rac2 < 10.0):
   #  rac1=rac1-360.0
   #if (rac4 > 350.0 and rac3 < 10.0):
   #  rac4=rac4-360.0
   #print corners(indict)

   return (ra0,dec0,rac1,decc1,rac2,decc2,rac3,decc3,rac4,decc4)
