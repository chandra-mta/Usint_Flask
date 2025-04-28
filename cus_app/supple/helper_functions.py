"""
**helper_functions.py**: Common functions used throughout the Usint application

:Author: W. Aaron (william.aaron@cfa.harvard.edu)
:Last Updated: Apr 28, 2025

"""
import sys
import os
import json
import itertools
import astropy.table

#
# --- Time Formats
#
OCAT_DATETIME_FORMAT = "%b %d %Y %I:%M%p"

def convert_row_to_dict(row):
    """convert an astropy table row into data formats expected by the application

    :param row: Sybase fetched astropy table row.
    :type row: Astropy.table.row.Row
    :returns: Formatted python dictionary
    :rtype: dict
    """
    row_dict = {col: row[col].tolist() for col in row.colnames}
    return row_dict

def convert_astropy_to_native(astropy_object, orient = None):
    """Converts an astropy object into python native objects.

    :param astropy_object: astropy object
    :type astropy_object: Table, Row, Column, ect.
    :param orient: Orientation of data Table conversion(uses pandas convention), defaults to None
    :type orient: str, optional
    """
    
    if isinstance(astropy_object, astropy.table.table.Table):
        #
        # --- Multiple possible orientations.
        # --- Similar argument to pandas dataframe for consistency but does not use pandas
        #
        if (orient == 'records') or (len(astropy_object) == 1 and orient is None):
            result = []
            for row in astropy_object:
                result.append(convert_row_to_dict(row))
            return result
        elif (orient == 'columns') or (len(astropy_object.colnames) == 1 and orient is None):
            result = {}
            for col in astropy_object.colnames:
                result[col] = astropy_object[col].tolist()
            return result
        elif len(astropy_object) == 0:
            raise ValueError("Cannot convert empty astropy table.")
        else:
            raise ValueError(f"Provide object orient [records, columns]. Provided orient: {orient}.")
            
    elif isinstance(astropy_object,astropy.table.row.Row):
        return convert_row_to_dict(astropy_object)
    
    elif isinstance(astropy_object, astropy.table.column.Column):
        return astropy_object.tolist()
    
    elif hasattr(astropy_object, 'tolist'):
        return astropy_object.tolist()