"""
**format_ocat_data.py**: Format ocat oriented data into Usint Form formats.

:Author: W. Aaron (william.aaron@cfa.harvard.edu)
:Last Updated: Mar 18, 2025

"""
import sys
import os


_OCAT_DATETIME_FORMAT = "%b %d %Y %I:%M%p"  #: NOTE Ocat dates are recorded without a leading zero. While datetime can process these dates, it never prints without a leading zero

_PULL_FORM_BY_CATEGORY = {
    "dither_param": [
        "dither_flag",
        "y_amp",
        "y_freq",
        "y_phase",
        "z_amp",
        "z_freq",
        "z_phase"
    ],
}
_NONE_FORM_EXCEPTIONS = ['dither_flag'] #: list of parameters to include in form initialization even if they are None.

def format_for_form(ocat_data):
    form = {}
    #
    #--- Initialize form values which are direct fetches from the ocat_data
    #
    for category, parameter_list in _PULL_FORM_BY_CATEGORY.items():
        form[category] = {}
        for param in parameter_list:
            val = ocat_data.get(param)
            if (val is not None) or (param in _NONE_FORM_EXCEPTIONS):
                form[category][param] = val
    #
    #--- Initialize category specific form parameters
    form = dither_additionals(form,ocat_data)
    return form

def synchronize_values(form):
    #
    #--- Perform RA, DEC, and Dither conversions of the editable form values to change the non-editable versions
    #
    if form.dither_param.dither_flag.data == 'Y':
        form.dither_param.y_amp.data = convert_from_arcsec(form.dither_param.y_amp_asec.data)
        form.dither_param.y_freq.data = convert_from_arcsec(form.dither_param.y_freq_asec.data)
        form.dither_param.z_amp.data = convert_from_arcsec(form.dither_param.z_amp_asec.data)
        form.dither_param.z_freq.data = convert_from_arcsec(form.dither_param.z_freq_asec.data)
    return form


#
#--- Dither Category Functions
#
def dither_additionals(form, ocat_data):
    keys = ('y_amp', 'y_freq', 'z_amp', 'z_freq')
    for key in keys:
        val = ocat_data.get(key)
        if val is not None:
            form['dither_param'][f'{key}_asec'] = convert_to_arcsec(ocat_data.get(key))
    return form

def convert_to_arcsec(degree):
    """convert degree value into arcsecs while retaining type

    :param degree: value in degrees
    :type degree: int, float, str
    :return: value in arcsecs
    :rtype: int, float, str
    """
    if isinstance(degree, float) or isinstance(degree, int):
        return round(degree * 3600,3)
    elif isinstance(degree,str):
        return str(round(float(degree)*3600,3))
    elif degree is None:
        return None

def convert_from_arcsec(arcsec):
    """convert arcsec value into degrees while retaining type

    :param arcsec: value in arcsecs
    :type arcsec: int, float, str
    :return: value in degrees
    :rtype: int, float, str
    """
    if isinstance(arcsec, float) or isinstance(arcsec, int):
        return round(arcsec / 3600,6)
    elif isinstance(arcsec,str):
        return str(round(float(arcsec)/3600, 6))
    elif arcsec is None:
        return None

