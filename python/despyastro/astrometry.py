"""

A collection of useful functions in astrometry. The functions ported
here correspond to a subset of inhereted from Felipe Menanteau's
astrometry.py old library. Removed all wcs/header transformations as
this are better handled by Erin Sheldon wcsutil

The functions will:
     - format decimal <---> DDMMSS/HHMMMSS
     - greater circle distance(ra,dec)
     - area in polygon

 Requires:
     numpy

 Felipe Menanteau, Apr/Oct 2014
 
"""

def circle_distance(ra1,dec1,ra2,dec2,units='deg'):
    """
    Calculates great-circle distances between the two points that is,
    the shortest distance over the earth's surface using the Haversine
    formula, see http://www.movable-type.co.uk/scripts/latlong.html
    """
    import numpy
    from math import pi
    
    cos   = numpy.cos
    sin   = numpy.sin
    acos  = numpy.arccos
    asin  = numpy.arcsin
    
    if units == 'deg':
        ra1  = ra1*pi/180.
        ra2  = ra2*pi/180.
        dec1 = dec1*pi/180.
        dec2 = dec2*pi/180.

    x = sin(dec1)*sin(dec2) + cos(dec1)*cos(dec2) * cos(ra2-ra1)
    x = numpy.where(x>1.0, 1, x) # Avoid x>1.0 values
    
    d = acos(x)
    if units == 'deg':
        d=d*180.0/pi
    return d

def deg2dec(deg,sep=":"):

    """
    Degrees to decimal, one element only.
    It should be generalized to an array or list of string.
    """

    vals = deg.split(sep)
    dd = float(vals[0])
    mm = float(vals[1])/60.
    ss = float(vals[2])/3600.

    if dd < 0:
        mm = -mm
        ss = -ss

    if vals[0] == '-00':
        mm = -mm
        ss = -ss

    return dd + mm + ss

def dec2deg(dec,short=None,sep=":"):

    """
    From decimal to degress, array or scalar
    """

    import numpy
    import sys
    
    dec = numpy.asarray(dec)
    # Keep the sign for later
    sig = numpy.where(dec < 0, -1, 1)

    dd = dec.astype("Int32")
    mm = (abs(dec-dd)*60).astype("Int32")
    ss = (abs(dec-dd)*60 - mm)*60

    # If not a scalar
    if len(dec.shape) != 0:

        x  =  numpy.concatenate((sig,dd,mm,ss))
        ids = numpy.where(abs(ss-60.) <= 1e-3)
        #print "IDS",ids
        ss[ids] = 0.0
        mm[ids] = mm[ids] + 1

        #n = len(dec)
        #x =  x.resize(3,len(dec)) # old numarray
        x =  numpy.resize(x,(4,len(dec)))
        #x.swapaxes(0,1) # old numarray
        x = numpy.swapaxes(x,0,1)
        if short:
            return map(format_deg_short,x)
        else:
            return map(format_deg_long,x)

    else:
        if float(abs(ss-60.)) < 1e-3 :
            ss = 0.0
            mm = mm + 1
        return format_deg( (sig,dd,mm,ss),short, sep)

    return

def dec2deg_short(dec):

    import numpy
    
    """
    From decimal to degress, array or scalar
    """

    dec = numpy.asarray(dec)
    dd = dec.astype("Int32")
    mm = (abs(dec-dd)*60).astype("Int32")
    ss = (abs(dec-dd)*60 - mm)*60
    x  =  numpy.concatenate((dd,mm,ss))

    # If not a scalar
    if len(dec.shape) != 0:

        ids = numpy.where(abs(ss-60.) <= 1e-3)
        print "IDS",ids
        ss[ids] = 0.0
        mm[ids] = mm[ids] + 1

        #n = len(dec)
        x =  x.resize(3,len(dec))
        x.swapaxes(0,1)
        return map(format_deg_short,x)

    else:
        if float(abs(ss-60.)) < 1e-3 :
            ss = 0.0
            mm = mm + 1
        return format_deg_short( (dd,mm,ss))

    return


def dec2deg_simple(dec):

    """From decimal to degrees, only scalar"""

    dd = int(dec)
    mm = int( abs(dec-dd)*60.)
    ss = (abs(dec-dd)*60 - mm)*60

    if abs(ss-60)< 1e-5:
        ss = 0.0
        mm = mm + 1
    return dd,mm,ss


def format_deg(x,short,sep=":"):

    if x[0]<0:
        sig = "-"
    else:
        sig = ""

    f1 = "%2d"

    if abs(float(x[1])) < 10: 
        f1 = "0%1d"
    else:
        f1 = "%2d"

    if float(x[2]) < 10: 
        f2 = "0%1d"
    else:
        f2 = "%2d"

    if float(x[3]) < 9.99:
        f3 = "0%.2f"
    else:
        f3 = "%.2f"

    if short=='ra':
        format = sig+f1+sep+f2+".%1d"
        return format % (abs(x[1]),x[2],int(x[3]/6))
    
    if short:
        format = sig+f1+sep+f2
        return format % (abs(x[1]),x[2])

    format = sig + f1+ sep +f2+ sep +f3
    return (format % (abs(x[1]),x[2],x[3]))[:-1]


# doesn't work for dec -00:01:23 ....
def format_deg_old(x,short,sep=":"):

    f1 = "%2d"

    if abs(float(x[0])) < 10: 
        f1 = "0%1d"
    else:
        f1 = "%2d"

    if float(x[1]) < 10: 
        f2 = "0%1d"
    else:
        f2 = "%2d"

    if float(x[2]) < 9.9:
        f3 = "0%.1f"
    else:
        f3 = "%.1f"

    if short:
        format = f1+sep+f2
        return format % (x[0],x[1])

    format = f1+ sep +f2+ sep +f3
    return format % (x[0],x[1],x[2])

def format_deg_long(x):
    return format_deg(x,short=None,sep=":")
    
def format_deg_short(x):

    if x[0]<0:
        sig = "-"
    else:
        sig = "+"
    
    if abs(float(x[1])) < 10: 
        f1 = "0%1d"
    else:
        f1 = "%2d"
        
    if abs(float(x[2])) < 10: 
        f2 = "0%1d"
    else:
        f2 = "%2d"

    if float(x[3]) < 10:
        f3 = "0%.1f"
    else:
        f3 = "%.1f"

    format = sig+f1+":"+f2
    return format % (abs(x[1]),x[2])



def sky_area(ra,dec,units='degrees'):

    """
    Based on: 'Computing the Area of a Spherical Polygon" by Robert D. Miller
    in "Graphics Gems IV', Academic Press, 1994
    
    http://users.soe.ucsc.edu/~pang/160/f98/Gems/GemsIV/sph_poly.c
    
    Translated from J.D. Smith's IDL routine spherical_poly_area
    Returns the area (solid angle) projected in the sky by a polygon with
    vertices (ra,dec) in degrees
    
    Doesn't work well on wide range of RA's
    """
    
    import math
    import numpy

    sterad2degsq = (180/math.pi)**2 # sterad --> deg2
    RADEG  = 180.0/math.pi          # rad    --> degrees
    HalfPi = math.pi/2.
    lam1   = ra/RADEG
    lam2   = numpy.roll(lam1,1)
    beta1  = dec/RADEG
    beta2  = numpy.roll(beta1,1)
    cbeta1 = numpy.cos(beta1)
    cbeta2 = numpy.roll(cbeta1,1)

    HavA=numpy.sin((beta2-beta1)/2.0)**2 + cbeta1*cbeta2*numpy.sin((lam2-lam1)/2.0)**2
    
    A= 2.0*numpy.arcsin(numpy.sqrt(HavA))         
    B= HalfPi-beta2              
    C= HalfPi-beta1              
    S= 0.5*(A+B+C)                
    T = numpy.tan(S/2.0) * numpy.tan((S-A)/2.0) * numpy.tan((S-B)/2.0) * numpy.tan((S-C)/2.0)

    lam = (lam2-lam1) + 2.0*math.pi*(numpy.where( lam1 >= lam2, 1, 0 ))

    Excess = numpy.abs(4.0*numpy.arctan(numpy.sqrt(numpy.abs(T)))) * (1.0 - 2.0*(numpy.where(lam > math.pi, 1.0 ,0.0 )))

    area = abs((Excess*numpy.where(lam2 != lam1,1,0)).sum())
    if units == 'degrees':
        area = area*sterad2degsq

    return area
