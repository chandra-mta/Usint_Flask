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
# --- Globals
#
ALL_NULL_SET = {None,'',' ','<Blank>','N/A','NA','NONE','NULL','Na','None','Null','none','null'}
OCAT_DATETIME_FORMAT = "%b %d %Y %I:%M%p"
USINT_DATETIME_FORMAT = "%b %d %Y %H:%M"
DATETIME_FORMATS = ['%m:%d:%Y:%H:%M:%S', '%m:%d:%Y:%H:%M', USINT_DATETIME_FORMAT, OCAT_DATETIME_FORMAT, '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M']
STORAGE_FORMAT = '%Y-%m-%dT%H:%M:%SZ' #: ISO 8601 format. Used in storage for Usint SQL Database

#
# --- Parameter selection for time, roll, and window ranks
#
TIME_RANK_PARAMS = {'window_constraint', 'tstart', 'tstop'}
ROLL_RANK_PARAMS = {'roll_constraint', 'roll_180', 'roll', 'roll_tolerance'}
WINDOW_RANK_PARAMS = {'chip', 'start_row', 'start_column', 'width', 'height', 'lower_threshold', 'pha_range', 'sample'}
ALL_RANK_PARAMS = TIME_RANK_PARAMS.union(ROLL_RANK_PARAMS).union(WINDOW_RANK_PARAMS)

#
# --- Coercion section. Converting the strings text to the correct data types.
#
def coerce_none(val):
    if val in ALL_NULL_SET:
        return None
    return val

def coerce_number(val):
    if not isinstance(val,(int,float)):
        try:
            val = int(val)
        except ValueError:
            try:
                val = float(val)
            except ValueError:
                pass
    return val

def coerce_time(val):
    if isinstance(val, str):
        x = val.replace('::', ':')
        if x[-1] == "Z":
            x = x[:-1]
        x = x.split('.')[0]
        for format in DATETIME_FORMATS:
            try:
                return datetime.strptime(x,format)
            except ValueError:
                pass
    return val

def coerce_json(val):
    """Coercion of python data type to a json-formatted string for data storage"""
    if val in ALL_NULL_SET:
        return None
    else:
        return json.dumps(val)

def coerce(val):
    #: Null section
    if val in ALL_NULL_SET:
        return None
    #: Number section
    val = coerce_number(val)
    if isinstance(val,(int,float)):
        return val
    #: Time section.
    val = coerce_time(val)
    if isinstance(val,datetime):
        return val
    #: Regular string
    return val
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