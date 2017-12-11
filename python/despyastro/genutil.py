"""
A set of general (for lack of better word) python utilities functions
that use numpy natively.
Felipe Menanteau, NCSA Oct 2014
"""
import collections

def query2dict_of_columns(query,dbhandle,array=False):

    """
    Transforms the result of an SQL query and a Database handle object [dhandle]
    into a dictionary of list or numpy arrays if array=True
    """ 

    if array: import numpy
    # Get the cursor from the DB handle
    cur = dbhandle.cursor()
    # Execute
    cur.execute(query)
    # Get them all at once
    list_of_tuples = cur.fetchall()
    # Get the description of the columns to make the dictionary
    desc = [d[0] for d in cur.description] 

    querydic = collections.OrderedDict() # We will populate this one
    cols = zip(*list_of_tuples)
    for k in range(len(cols)):
        key = desc[k]
        if array:
            if isinstance(cols[k][0],str):
                querydic[key] = numpy.array(cols[k],dtype=object)
            else:
                querydic[key] = numpy.array(cols[k])
        else:
            querydic[key] = cols[k]    
    return querydic 

def query2rec(query,dbhandle,verb=False):
    """
    Queries DB and returns results as a numpy recarray.
    """ 

    import numpy
    # Get the cursor from the DB handle
    cur = dbhandle.cursor()
    # Execute
    cur.execute(query)
    tuples = cur.fetchall()

    # Return rec array                                                                                                                                          
    if len(tuples)>0:
        names  = [d[0] for d in cur.description]
        return numpy.rec.array(tuples,names=names)
    else:
        if verb: print "# WARNING DB Query in query2rec() returned no results"
	return False
