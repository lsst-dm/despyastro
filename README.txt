
A collection of astro-related Python functions useful for DESDM
Python-based modules. This modules has evolved from the orginal
despyutils that was growing to be too large and have too many
dependencies. 

 Felipe Menanteau, October 2014.

Requires:
   numpy
   scipy

Changes:

-- version 0.1.0 
First version for despyastro migrated from despyutils

-- version 0.2.0
Added genutils, migrated partly from despyutils

-- version 0.3.0 (Dec 2014).
Added query2rec(query,dbhandle) (by Alex Drlica-Wagner) to genutils.py
and made genutils visible at root via _init__.py

-- version 0.3.1 (July 2015)
Re-worked function to transform dec2deg and deg2dec in astrometry
Added function to get pixel-scale from fitsheader matrix CDXX

-- version 0.3.2 (July 2015)
Minor changes to the  genutils.query2rec() function that now returns
False (instead of crashing) when the query returns empty.
