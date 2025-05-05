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
from astropy.coordinates import Angle
#
# --- Classes
#
class IterateRecords:
    """Iterating through a records oriented object"""
    def __init__(self,list1, list2):
        self.list1 = list1
        self.list2 = list2
        self.top_level_iterator = enumerate(itertools.zip_longest(self.list1 or [],self.list2 or [],fillvalue={}))
        _ = next(self.top_level_iterator)
        self.order = _[0]
        self.inner_iterator = itertools.zip_longest(_[1][0].keys() or _[1][1].keys(),
                                                                   _[1][0].values(),
                                                                   _[1][1].values(),
                                                                  fillvalue=None)
    def __iter__(self):
        return self

    
    def __next__(self):
        try:
            param, org, req = next(self.inner_iterator)
            return self.order, param, org, req
        except StopIteration:
            _ = next(self.top_level_iterator)
            self.order = _[0]
            self.inner_iterator = itertools.zip_longest(_[1][0].keys() or _[1][1].keys(),
                                                                       _[1][0].values(),
                                                                       _[1][1].values(),
                                                                      fillvalue=None)
            
        return self.__next__()

class IterateColumns:
    """Iterating through a columns oriented object"""
    
    def __get_more__(self,obj,key):
        if obj == None:
            return None
        else:
            return obj[key]
    
    def __init__(self,dict1, dict2):
        self.dict1 = dict1
        self.dict2 = dict2
        self.top_level_iterator = iter(self.dict1.keys() or self.dict2.keys())
        _ = next(self.top_level_iterator)
        self.parameter = _
        self.inner_iterator = enumerate(itertools.zip_longest(get_more(self.dict1, _) or [],
                                                                 get_more(self.dict2, _) or [],
                                                                 fillvalue=None
                                                                ))
    def __iter__(self):
        return self

    
    def __next__(self):
        try:
            i, (org, req) = next(self.inner_iterator)
            return i, self.parameter, org, req
        except StopIteration:
            _ = next(self.top_level_iterator)
            self.parameter = _
            self.inner_iterator = enumerate(itertools.zip_longest(get_more(self.dict1, _) or [],
                                                                 get_more(self.dict2, _) or [],
                                                                 fillvalue=None
                                                                ))
            
        return self.__next__()

#
# --- Globals
#
NULL_LIST = [None,'',' ','<Blank>','N/A','NA','NONE','NULL','Na','None','Null','none','null']
OCAT_DATETIME_FORMAT = "%b %d %Y %I:%M%p" #: Warning Ocat Datetimes are stored without a leading zero in the day. This can cause python comparisons to fail
USINT_DATETIME_FORMAT = "%b %d %Y %H:%M"
STORAGE_FORMAT = '%Y-%m-%dT%H:%M:%SZ' #: ISO 8601 format. Used in storage for Usint SQL Database
DATETIME_FORMATS = [USINT_DATETIME_FORMAT, OCAT_DATETIME_FORMAT, STORAGE_FORMAT, '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M','%m:%d:%Y:%H:%M:%S', '%m:%d:%Y:%H:%M', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M',]

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
    if isinstance(val, (list, tuple)):
        return [coerce_none(x) for x in val]
    elif isinstance(val, dict):
        return {k:coerce_none(v) for k,v in val.items()}
    elif val in NULL_LIST:
        return None
    return val

def coerce_number(val):
    if not isinstance(val,(int,float)):
        try:
            val = int(val)
        except (ValueError, TypeError):
            try:
                val = float(val)
            except (ValueError, TypeError):
                pass
    return val

def coerce_time(val):
    """Parse a variety of different time formats across CXC tools and data sources"""
    if isinstance(val, str):
        x = val.replace('::', ':')
        x = x.split('.')[0]
        for format in DATETIME_FORMATS:
            try:
                return datetime.strptime(x,format).strftime(STORAGE_FORMAT)
            except ValueError:
                pass
    return val

def coerce_json(val):
    """Coercion of python data type to a json-formatted string for data storage"""
    if val in NULL_LIST:
        return None
    elif isinstance(val, datetime):
        #: Convert to ISO 8601 string then store
        return json.dumps(val.strftime(STORAGE_FORMAT))
    elif isinstance(val, list):
        if len(val) > 0 and isinstance(val[0], datetime):
            return json.dumps([x.strftime(STORAGE_FORMAT) for x in val])
        else:
            return json.dumps(val)
    else:
        return json.dumps(val)

def coerce(val):
    if isinstance(val, (list, tuple)):
        return [coerce(x) for x in val]
    elif isinstance(val, dict):
        return {k:coerce(v) for k,v in val.items()}
    #: Null section
    elif val in NULL_LIST:
        return None
    #: Number section
    val = coerce_number(val)
    if isinstance(val,(int,float)):
        return val
    #: Time section if applicable
    val = coerce_time(val)
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
    elif isinstance(first, (float,int)) and isinstance(second, (float,int)):
        if abs(first - second) < 0.000001:
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
    if ranks in (None, [], {}):
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

#
# --- Calculative Functions
#
def convert_ra_dec_format(dra, ddec, oformat):
    """
    convert ra/dec format
    input:  dra     --- either <hh>:<mm>:<ss> or <dd.ddddd> format
            ddec    --- either <dd>:<mm>:<ss> or <ddd.ddddd> format
            oformat --- specify output format as either 'dd', or 'hmsdms'

    output: tra     --- either <hh>:<mm>:<ss> or <dd.ddddd> format
            tdec    --- either <dd>:<mm>:<ss> or <ddd.ddddd> format
    """
    if dra is None and ddec is None:
        return None, None
    #
    #--- Define input format
    #
    if ":" in str(ddec):
        iformat = 'hmsdms'
    else:
        iformat = 'dd'
    #
    #--- Switch formats
    #
    if iformat == 'dd' and oformat == 'hmsdms':
        angle_ra = Angle(f"{dra} degrees")
        tra = str(angle_ra.to_string(sep=":",pad=True,precision=4,unit='hourangle'))
        angle_dec = Angle(f"{ddec} degrees")
        tdec = str(angle_dec.to_string(sep=":",pad=True,precision=4,alwayssign=True,unit='degree'))
    elif iformat == 'hmsdms' and oformat == 'dd':
        angle_ra = Angle(f"{dra} hours")
        tra = float(angle_ra.to_string(decimal=True,precision=6,unit='degree'))
        angle_dec = Angle(f"{ddec} degrees")
        tdec = float(angle_dec.to_string(decimal=True,precision=6,unit='degree'))
    else:
        return dra, ddec
    
    return tra,tdec

def rank_ordr(ranks):
    if ranks is None:
        return 0
    elif isinstance(ranks, list):
        #: records orientation
        return len(ranks)
    elif isinstance(ranks, dict):
        #: Columns orientation
        return max([len(v) for v in ranks.values()])
