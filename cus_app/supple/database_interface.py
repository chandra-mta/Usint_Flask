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
import os
from datetime import datetime
import json
from math import sqrt
from sqlalchemy import select, desc, case, text
from sqlalchemy.orm.exc import NoResultFound
from cus_app import db
from cus_app.models import User, Revision, Signoff, Parameter, Request, Original
from flask_login import current_user
from cus_app.supple.helper_functions import coerce_json, DATETIME_FORMATS, is_open

stat_dir =  os.path.join(os.path.dirname(os.path.abspath(__file__)),'..', 'static')
with open(os.path.join(stat_dir, 'parameter_selections.json')) as f:
    _PARAM_SELECTIONS = json.load(f)

def construct_revision(obsid,ocat_data,kind,org_dict = {},req_dict = {}):
    """
    Generate a Revision ORM object based on the provided obsid information
    """
    rev_no = find_next_rev_no(obsid)
    curr_epoch = int(datetime.now().timestamp())
    #: Identify Notes
    if kind == 'norm':
        notes = construct_notes(org_dict, req_dict)
    else:
        notes = None
    revision = Revision(obsid = int(obsid),
                    revision_number = rev_no,
                    kind = kind,
                    sequence_number = ocat_data.get('seq_nbr'),
                    time = curr_epoch,
                    user_id = current_user.id,
                    notes = notes
                    )
    return revision

def construct_notes(org_dict, req_dict):
    """
    Construct notes json based on change requests
    """
    notes = {}
    ra = None
    dec = None
    ora = None
    odec = None
    for param, val in req_dict.items():
        if param == 'targname':
            notes.update({'target_name_change':True})
        elif param == 'comments':
            notes.update({'comment_change': True})
        elif param == 'instrument':
            notes.update({'instrument_change': True})
        elif param == 'grating':
            notes.update({'grating_change': True})
        elif param in ('dither_flag', 'window_flag', 'roll_flag', 'spwindow_flag'):
            notes.update({'flag_change': True})
        elif param == 'ra':
            ra = val
        elif param == 'dec':
            dec = val
    if ra is not None or dec is not None:
        ora = org_dict.get('ra')
        if ra is None:
            ra = ora
        odec = org_dict.get('dec')
        if dec is None:
            dec = odec
        if ora != 0 and odec != 0 and is_large_coord_shift(ra,dec, ora, odec):
                notes.update({'large_coordinate_change': True})
    
    if len(notes) > 0:
        return json.dumps(notes)
    else:
        return None

def is_large_coord_shift(ra,dec, ora, odec):
    if ora is None or odec is None:
        return False
    diff = sqrt((ora -ra)**2 + (odec - dec)**2)
    if diff > 0.1333:
        return True
    else:
        return False

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

def perform_signoff(signoff_id, signoff_kind):
    """
    Update the signoff entry matching to the provided id

    :param signoff_kind: String determining the kind of signoff to provide (gen, acis, acis_si, hrc_si, usint, approve)
    """
    signoff_id = int(signoff_id)
    curr_epoch = int(datetime.now().timestamp())
    signoff_obj = db.session.execute(select(Signoff).where(Signoff.id == signoff_id)).scalar_one()
    if signoff_kind == 'gen':
        signoff_obj.general_status = 'Signed'
        signoff_obj.general_signoff_id = current_user.id
        signoff_obj.general_time = curr_epoch
    elif signoff_kind == 'acis':
        signoff_obj.acis_status = 'Signed'
        signoff_obj.acis_signoff_id = current_user.id
        signoff_obj.acis_time = curr_epoch
    elif signoff_kind == 'acis_si':
        signoff_obj.acis_si_status = 'Signed'
        signoff_obj.acis_si_signoff_id = current_user.id
        signoff_obj.acis_si_time = curr_epoch
    elif signoff_kind == 'hrc_si':
        signoff_obj.hrc_si_status = 'Signed'
        signoff_obj.hrc_si_signoff_id = current_user.id
        signoff_obj.hrc_si_time = curr_epoch
    elif signoff_kind in ('usint', 'approve'):
        signoff_obj.usint_status = 'Signed'
        signoff_obj.usint_signoff_id = current_user.id
        signoff_obj.usint_time = curr_epoch
        if signoff_kind == 'approve':
            #: Additionally create an approval revision and signoff.
            matching_rev = signoff_obj.revision
            new_revision = Revision(obsid = matching_rev.obsid,
                                    revision_number = find_next_rev_no(matching_rev.obsid),
                                    kind = 'asis',
                                    sequence_number = matching_rev.sequence_number,
                                    time = curr_epoch,
                                    user_id = current_user.id
            )
            new_signoff = construct_auto_signoff(new_revision)
            db.session.add(new_revision)
            db.session.add(new_signoff)
    db.session.commit()

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

def user_by_name(name):
    return db.session.execute(select(User).where(User.username == name)).scalars().first()

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

def pull_revision(order_by = {'id': 'asc'}, **kwargs):
    """
    Fetch list of recent revisions based on kwarg criteria
    """
    #
    # --- Starting query object
    #
    query = select(Revision)
    
    #
    # --- Kwarg processing is ordered by order of execution (WHERE, ORDER_BY, LIMIT)
    #
    before = _to_epoch(kwargs.pop('before', None))
    if before is not None:
        query = query.where(Revision.time <= before)
        
    after = _to_epoch(kwargs.pop('after', None))
    if after is not None:
        query = query.where(Revision.time >= after)
    
    limit = kwargs.pop('limit', None)
    if limit is not None:
        query = query.limit(limit)
    #
    # --- Assumed the remaining unidentified kwargs are WHERE column equality searches
    # --- which will still execute before the ORDER_BY and LIMIT statements in the SQL query,
    # --- but the SQLAlchemy query builder will list these ones after the 'before', 'after' wheres
    #
    query = query.filter_by(**kwargs)
    
    #: By default, order the query by descending Revision ID number so that the end result order
    #: contains a suborder of returning the most recently made revisions first.
    ordering = ",".join([f"{k} {v}" for k,v in order_by.items()])
    query = query.order_by(text(ordering))
    return db.session.execute(query).scalars().all()

def pull_status(limit = 200, **kwargs):
    """Special version of the pull_revision function tailored for the target parameter status page.

    :param limit: _description_, defaults to 200
    :type limit: int, optional
    :return: Recent (Revision, Signoff) in descending order.
    """
    if 'order_user' in kwargs.keys():
        #: Order by listing the target user id first, then the rest in descending order
        order_user = int(kwargs['order_user'])
        query = select(Revision, Signoff).join(Revision.signoff).order_by(case((Revision.user_id == order_user, 0),else_=1)).order_by(desc(Revision.id)).limit(limit)

    elif kwargs.get('order_obsid'):
        #: Special case in which we must first subquery the most recent LIMIT number of revisions, then sort by obsid
        subquery = select(Revision.id).order_by(desc(Revision.id)).limit(limit).subquery()
        query = select(Revision, Signoff).join(Revision.signoff).select_from(Revision, subquery).where(Revision.id == subquery.c.id).order_by(Revision.obsid).order_by(desc(Revision.revision_number))
    else:
        #: Default descending order
        query = select(Revision, Signoff).join(Revision.signoff).order_by(desc(Revision.id)).limit(limit)
    return db.session.execute(query).all()

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

def has_open_revision(obsid):
    """
    Check database for whether there is an open revision for the approval process
    """
    result = db.session.execute(select(Revision, Signoff).join(Revision.signoff).where(Revision.obsid == obsid)).all()
    has_open_revision = False
    for revs, signs in result:
        if is_open(signs):
            has_open_revision = True
            break
    return has_open_revision

def _to_epoch(time):
    """
    Convert variety of time input to epoch time
    """
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