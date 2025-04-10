"""
**format_ocat_data.py**: Format ocat oriented data into Usint Form formats.

:Author: W. Aaron (william.aaron@cfa.harvard.edu)
:Last Updated: Mar 18, 2025

"""
from astropy.coordinates import Angle
from datetime import datetime

_OCAT_DATETIME_FORMAT = "%b %d %Y %I:%M%p"  #: NOTE Ocat dates are recorded without a leading zero. While datetime can process these dates, it never prints without a leading zero
_COMBINE_DATETIME_FORMAT = "%b%d%Y%H:%M"
_NULL_LIST = (None, 'None', '', [])

def generate_additionals(ocat_data):
    """Convert certain ocat data parameters to new values for form editing

    :param ocat_data: Ocat Data keyed by parameter directly (Represents only what's in the ocat in original form)
    :type ocat_data: dict(str, value)
    """
    additional = {}
    #
    #--- RA, Dec
    #
    ra = ocat_data.get('ra')
    dec = ocat_data.get('dec')
    if ra is not None and dec is not None:
        ra_hms, dec_dms = convert_ra_dec_format(ra, dec, 'hmsdms')
        additional['ra_hms'] = ra_hms
        additional['dec_dms'] = dec_dms
    #
    # --- Dither
    #
    for key in ('y_amp', 'y_freq', 'z_amp', 'z_freq'):
        val = ocat_data.get(key)
        if val is not None:
            additional[f'{key}_asec'] = val * 3600

def convert_ra_dec_format(dra, ddec, oformat):
    """
    convert ra/dec format
    input:  dra     --- either <hh>:<mm>:<ss> or <dd.ddddd> format
            ddec    --- either <dd>:<mm>:<ss> or <ddd.ddddd> format
            oformat --- specify output format as either 'dd', or 'hmsdms'

    output: tra     --- either <hh>:<mm>:<ss> or <dd.ddddd> format
            tdec    --- either <dd>:<mm>:<ss> or <ddd.ddddd> format
    """
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
        tra = angle_ra.to_string(sep=":",pad=True,precision=4,unit='hourangle')
        angle_dec = Angle(f"{ddec} degrees")
        tdec = angle_dec.to_string(sep=":",pad=True,precision=4,alwayssign=True,unit='degree')
    elif iformat == 'hmsdms' and oformat == 'dd':
        angle_ra = Angle(f"{dra} hours")
        tra = float(angle_ra.to_string(decimal=True,precision=6,unit='degree'))
        angle_dec = Angle(f"{ddec} degrees")
        tdec = float(angle_dec.to_string(decimal=True,precision=6,unit='degree'))
    else:
        return dra, ddec
    
    return tra,tdec


def coerce(value):
    def _coerce_single(value):
        if isinstance(value,(int,float)):
            return value #: No coercion necessary
        try: 
            value = int(value)
            return value
        except (ValueError, TypeError):
            pass
        try:
            value = float(value)
            return value
        except (ValueError, TypeError):
            pass
        try:
            value = datetime.strptime(value,_OCAT_DATETIME_FORMAT)
            return value
        except (ValueError, TypeError):
            pass
        try:
            value = datetime.strptime(value,_COMBINE_DATETIME_FORMAT)
            return value
        except (ValueError, TypeError):
            pass
        if value in _NULL_LIST:
            return None #: Apply as coerce argument to any field to cast None to correct data type
        return value #: Simple string
    if isinstance(value,list):
        if value == []:
            return None
        else:
            value_list = [_coerce_single(x) for x in value]
        return value_list
    else:
        return _coerce_single(value)

def format_for_comparison(form):
    """
    Format the Flask Form into a coerced dictionary to compare with ocat_data.
    Also contains the labels used for the comparison.
    """
    def _determine_include(field):
        _DO_INCLUDE = ['ra', 'dec', 'y_amp', 'y_freq', 'z_amp', 'z_freq']
        _DONT_INCLUDE = []
        if field.render_kw['readonly']:
            include = False
        if field.name.split('-')[-1] in _DO_INCLUDE:
            include = True
        elif field.name.split('-')[-1] in _DONT_INCLUDE:
            include = False

    for subfield in form:
        if subfield.type == 'FormField':
            for parameter_field in subfield:
                pass

    form_dict = form.data
    for category, value in form_dict.items():
        if isinstance(value,dict): #: Handling parameter dictionary
            for param, data in value.items():
                form_dict[category][param] = coerce(data)
        else:
            form_dict[category] = coerce(value)
    return form_dict