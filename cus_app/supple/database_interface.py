"""
Database Interface
==============

**database_interface.py**: Set of functions interfacing with the Usint database

:Author: W. Aaron (william.aaron@cfa.harvard.edu)
:Last Updated: May 01, 2025


:NOTE: Some of the ORM construction functions operate on the SQLalchemy.orm.relationship() mapping to instantiate parameters,
while others reference foreign and primary keys directly. This is because the relationship() mapping requires related ORM's to be added to the database session
before instantiation if the relationship mapped key has the NON NULL constraint. Therefore, it's more reliable to instantiate with the primary key id's directly
for web interface transactions. 
"""
import sys
import os
from datetime import datetime
import json
from sqlalchemy import select, insert, desc
from sqlalchemy.orm.exc import NoResultFound
from cus_app import db
from cus_app.models     import register_user, User, Revision, Signoff, Parameter, Request, Original
from flask_login    import current_user
from cus_app.supple.helper_functions import coerce_json, DATETIME_FORMATS

stat_dir =  os.path.join(os.path.dirname(os.path.abspath(__file__)),'..', 'static')
with open(os.path.join(stat_dir, 'parameter_selections.json')) as f:
    _PARAM_SELECTIONS = json.load(f)

def construct_revision(obsid,ocat_data,kind):
    """
    Generate a Revision ORM object based on the provided obsid information
    """
    rev_no = find_next_rev_no(obsid)
    curr_epoch = int(datetime.now().timestamp())
    revision = Revision(obsid = int(obsid),
                    revision_number = rev_no,
                    kind = kind,
                    sequence_number = ocat_data.get('seq_nbr'),
                    time = curr_epoch,
                    user = current_user
                    )
    return revision

def construct_signoff(rev_obj, req_dict={}):
    """
    Determine the Signoffs entry based on the revision object based in kind:(norm, asis, remove, clone).
    The signoff status options are : ('Signed', 'Not Required', 'Pending', 'Discard').
    signoff time is the epoch time of when the signoff was made.
    The signoff itself lists the user id.
    """
    
    if rev_obj.kind in ('asis', 'remove'):
        #:Adding or removing from the approved list. Auto signoff with Usint revision performing user.
        signoff = construct_auto_signoff(rev_obj)
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

def construct_auto_signoff(rev_obj):
    """
    Automatically fill a usint signoff ORM without other signoffs.
    """
    curr_epoch = int(datetime.now().timestamp())
    signoff = Signoff(revision = rev_obj,
                            general_status = 'Not Required',
                            acis_status = 'Not Required',
                            acis_si_status = 'Not Required',
                            hrc_si_status = 'Not Required',
                            usint_status = 'Signed',
                            usint_signoff_id = rev_obj.user_id,
                            usint_time = curr_epoch
                    )
    return signoff

def construct_requests(rev_obj, req_dict):
    """
    Construct a list of Request ORM's for insertion.
    """
    all_requests = []
    for key, value in req_dict.items():
        if key in _PARAM_SELECTIONS["general_signoff_params"] + _PARAM_SELECTIONS["acis_signoff_params"] + _PARAM_SELECTIONS["acis_si_signoff_params"] + _PARAM_SELECTIONS["hrc_si_signoff_params"]:
            param = pull_param(key)
            req = Request(revision_id= rev_obj.id,
                        parameter_id = param.id,
                        value = coerce_json(value)
            )
            all_requests.append(req)
    return all_requests

def construct_originals(rev_obj, org_dict):
    """
    Construct a list of Original ORM's for insertion. Only adding non-null values as null is inferred.
    """
    all_originals = []
    for key, value in org_dict.items():
        if value is not None:
            if key in _PARAM_SELECTIONS["general_signoff_params"] + _PARAM_SELECTIONS["acis_signoff_params"] + _PARAM_SELECTIONS["acis_si_signoff_params"] + _PARAM_SELECTIONS["hrc_si_signoff_params"]:
                param = pull_param(key)
                req = Original(revision_id= rev_obj.id,
                            parameter_id = param.id,
                            value = coerce_json(value)
                )
                all_originals.append(req)
    return all_originals

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

def pull_param(param):
    """
    Fetch the Parameter ORM by name.
    Will return an SQLAlchemy.orm.exc.NoResultFound if the parameter is not in the table
    """
    try:
        result = db.session.execute(select(Parameter).where(Parameter.name == param)).scalar_one()
    except NoResultFound:
        #: Return same error with more specifics
        raise NoResultFound(f"No result for '{param}' parameter search in table.")

    return result

def pull_revision(**kwargs):
    """
    Fetch list of recent revisions based on kwarg criteria
    """
    def _to_epoch(time):
        if time is None:
            return None
        elif isinstance(time,(int, float)):
            return time
        elif isinstance(time, datetime):
            return time.timestamp()
        elif isinstance(time,str):
            x = time.replace('::', ':')
            x = x.split('.')[0]
            for format in DATETIME_FORMATS:
                try:
                    return datetime.strptime(x,format).timestamp()
                except ValueError:
                    pass
    #
    # --- Fetch by recent number
    #
    last = kwargs.get('last')
    if last is not None:
        return db.session.execute(select(Revision).order_by(desc(Revision.id)).limit(last)).all()

    #
    # --- Fetch by time interval
    #
    before = _to_epoch(kwargs.get('before'))
    after = _to_epoch(kwargs.get('after'))
    if before is None and after is not None:
        return db.session.execute(select(Revision).where(Revision.time >= after).order_by(desc(Revision.id))).all()
    elif before is not None and after is None:
        return db.session.execute(select(Revision).where(Revision.time <= before).order_by(desc(Revision.id))).all()
    elif before is not None and after is not None:
        return db.session.execute(select(Revision).where(Revision.time <= before).where(Revision.time >= after).order_by(desc(Revision.id))).all()        

    
def pull_signoff(rev_obj):
    """
    Fetch signoff matching provides revision
    """
    result = db.session.execute(select(Signoff).where(Signoff.revision_id == rev_obj.id)).scalar_one()
    return result

def find_next_rev_no(obsid):
    """
    Find the revisions for the provided obsid in the listed revision table, and identify the next revision number
    """
    revision_numbers = db.session.execute(select(Revision.revision_number).where(Revision.obsid == obsid)).scalars().all()
    if len(revision_numbers) == 0:
        return 1
    else:
        return max(revision_numbers) + 1


def is_approved(obsid):
    """
    Check whether an obsid is listed as approved in the usint database
    """
    obsid = int(obsid)
    revision_result = db.session.execute(db.select(Revision).where(Revision.obsid==obsid).order_by(Revision.revision_number)).scalars().all()
    is_approved = False
    for rev in revision_result:
        if rev.kind == 'asis':
            is_approved = True
        elif rev.kind == 'remove':
            is_approved = False
    return is_approved