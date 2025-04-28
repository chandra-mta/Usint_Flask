"""
**helper_functions.py**: Common functions used throughout the Usint application

:Author: W. Aaron (william.aaron@cfa.harvard.edu)
:Last Updated: Apr 28, 2025

"""
import sys
import os
import json
import itertools
from datetime import datetime
import astropy.table

#
# --- Time Formats
#
OCAT_DATETIME_FORMAT = "%b %d %Y %I:%M%p"

#
# --- Fetching Functions
#
def get_more(obj,key):
    if obj is None:
        return None
    else:
        if isinstance(obj,dict):
            return object.get(key)
        else:
            return obj[key]
#
# --- Comparison Functions
#
def approx_equals(first,second):
    """
    Compare values within reason for a revision. Return True if they are close enough to equal
    """
    if first is None and second is not None:
        return False
    elif first is not None and second is None:
        return False
    elif first is None and second is None:
        return True
    elif isinstance(first, (float,int)):
        if abs(first - second) < 0.000001:
            return True
        else:
            return False
    elif isinstance(first, str):
        if first == second:
            return True
        else:
            return False
    elif isinstance(first,datetime) and isinstance(second,datetime):
        diff = (second - first).total_seconds()
        return diff > 60
    elif isinstance(first, list) and isinstance(second, list):
        if len(first) != len(second):
            return False
        _result = True
        for i,j in zip(first,second):
            if not approx_equals(i,j):
                _result = False
                break
        return _result
    elif isinstance(first, dict) and isinstance(second, dict):
        first_keys = set(first.keys())
        second_keys = set(second.keys())
        if first_keys != second_keys:
            return False
        _result = True
        for key in first_keys:
            if not approx_equals(first[key], second[key]):
                _result = False
                break
        return _result
    else:
        return first == second

#
#--- Conversion Functions
#
def reorient_rank(ranks, orient):
    """
    Reorient a set of ranks, similar to how convert_astropy_to_native() operates.
    But this alters a set of python natives rather than an astropy table.
    
    'records' is an ordered list of ranks, each entry being a dictionary of parameter name to value for that numbered rank
    'columns' is a dictionary of parameter columns, each entry matching an ordered list of values
    """
    if ranks is None:
        return None
    if orient not in ('records', 'columns'):
        raise ValueError(f"Provide object orient [records, columns]. Provided orient: {orient}.")
    
    if isinstance(ranks,list) and ranks != []:
        #: Is records
        if orient == 'records':
            return ranks
        else:
            columns = {}
            for key, value in ranks[0].items():
                columns[key] = [value]
            for i in range(1,len(ranks)):
                for key, value in ranks[i].items():
                    columns[key].append(value)
        return columns
                    
    elif isinstance(ranks,dict) and ranks != {}:
        #: Is columns
        if orient == 'columns':
            return ranks
        else:
            records = []
            key_list = list(ranks.keys())
            for i in range(len(ranks[key_list[0]])):
                rec = {}
                for key in key_list:
                    rec[key] = ranks[key][i]
                records.append(rec)
        return records
    else:
        raise ValueError(f"Incompatible Rank Object: {ranks}")

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