"""
Database Interface
==============

**database_interface.py**: Set of functions interfacing with the Usint database

:Author: W. Aaron (william.aaron@cfa.harvard.edu)
:Last Updated: May 01, 2025

"""
import sys
import os
from datetime import datetime
import json
from sqlalchemy import select, insert
from cus_app import db
from cus_app.models     import register_user, User, Revision, Signoff, Parameter, Request, Original
from flask_login    import current_user

stat_dir =  os.path.join(os.path.dirname(os.path.abspath(__file__)),'..', 'static')
with open(os.path.join(stat_dir, 'parameter_selections.json')) as f:
    _PARAM_SELECTIONS = json.load(f)

def construct_revision(obsid,ocat_data,kind):
    """
    Generate a Revision ORM object based on the provided obsid information
    """
    rev_no = find_next_rev_no(obsid)
    curr_epoch = int(datetime.now().timestamp())
    revision = Revision(obsid = obsid,
                    revision_number = rev_no,
                    kind = kind,
                    sequence_number = ocat_data.get('seq_nbr'),
                    time = curr_epoch,
                    user = current_user
                    )
    return revision

def construct_signoffs(rev_obj, req_dict={}):
    """
    Determine the Signoffs entry based on the revision object based in kind:(norm, asis, remove, clone).
    The signoff status options are : ('Signed', 'Not Required', 'Pending', 'Discard').
    signoff time is the epoch time of when the signoff was made.
    The signoff itself lists the user id.
    """
    curr_epoch = int(datetime.now().timestamp())
    if rev_obj.kind in ('asis', 'remove'):
        #:Adding or removing from the approved list. Auto signoff with Usint revision performing user.
        signoff = Signoff(revision = rev_obj,
                            general_status = 'Not Required',
                            acis_status = 'Not Required',
                            acis_si_status = 'Not Required',
                            hrc_si_status = 'Not Required',
                            usint_status = 'Signed',
                            usint_signoff_id = rev_obj.user_id,
                            usint_time = curr_epoch
                    )
    elif rev_obj.kind == 'clone':
        #: Needs ArcOps and Usint Signoff
        signoff = Signoff(revision = rev_obj,
                            general_status = 'Pending',
                            acis_status = 'Not Required',
                            acis_si_status = 'Not Required',
                            hrc_si_status = 'Not Required',
                            usint_status = 'Pending',
                    )
    elif rev_obj.kind == 'norm':
        #: Determine based on change requests linked to the revision object
        gen, acis, acis_si, hrc_si =  determine_signoff(req_dict)
        signoff = Signoff(revision=rev_obj,
                          general_status = gen,
                          acis_status = acis,
                          acis_si_status = acis_si,
                          hrc_si_status = hrc_si,
                          usint_status = 'Pending'
        )
    return signoff

def determine_signoff(req_dict):
    """
    Read the requested changes and determine what kind of signoff is necessary.
    """
    gen = 'Not Required'
    acis = 'Not Required'
    acis_si = 'Not Required'
    hrc_si = 'Not Required'
    #: Iterate through the requested parameter changes and define their signoff.
    for key in req_dict.keys():
        if key in _PARAM_SELECTIONS['general_signoff_params']:
            gen = 'Pending'
        if key in _PARAM_SELECTIONS['acis_signoff_params']:
            acis = 'Pending'
        if key in _PARAM_SELECTIONS['acis_si_signoff_params']:
            acis_si = 'Pending'
        if key in _PARAM_SELECTIONS['hrc_si_signoff_params']:
            hrc_si = 'Pending'
    return gen, acis, acis_si, hrc_si


def find_next_rev_no(obsid):
    """
    Find the revisions for the provided obsid in the listed revision table, and identify the next revision number
    """
    revision_numbers = db.session.execute(select(Revision.revision_number).where(Revision.obsid == obsid)).scalars().all()
    if len(revision_numbers) == 0:
        return 1
    else:
        return max(revision_numbers) + 1