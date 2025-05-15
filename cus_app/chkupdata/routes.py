"""
Parameter Check Page
==============

**chkupdata/routes.py**: Render the parameter Check Page

:Author: W. Aaron (william.aaron@cfa.harvard.edu)
:Last Updated: May 13, 2025

"""
import os
import json
from datetime import datetime, timedelta

from flask import render_template, request, session, redirect, url_for, flash
from flask_login import current_user

from cus_app.models import register_user
from cus_app.chkupdata import bp
from cus_app.chkupdata.forms import ObsidRevForm
import cus_app.supple.database_interface as dbi
import cus_app.supple.read_ocat_data as rod
from cus_app.supple.helper_functions import reorient_rank , rank_ordr

stat_dir =  os.path.join(os.path.dirname(os.path.abspath(__file__)),'..', 'static')
with open(os.path.join(stat_dir, 'labels.json')) as f:
    _LABELS = json.load(f)
with open(os.path.join(stat_dir, 'parameter_selections.json')) as f:
    _PARAM_SELECTIONS = json.load(f)

@bp.before_app_request
def before_request():
    if not current_user.is_authenticated:
        register_user()

@bp.route('/<obsidrev>', methods=['GET'])
@bp.route('/index/<obsidrev>', methods=['GET'])
def index(obsidrev):
    """
    Display the Target Parameter Status Page
    """
    try:
        obsid, rev = [int(x) for x in obsidrev.split('.')]
    except (ValueError, TypeError):
        flash(f"Ill-formatted Obsid.Rev. {obsidrev}")
        return redirect(url_for('chkupdata.provide_obsidrev'))
    
    revision_list = dbi.pull_revision(order_by={'revision_number': 'asc'}, obsid = obsid)
    #: Pop out the revision we are interested in, then use the rest to construct related links for the webpage.
    revision = None
    for i in range(len(revision_list)):
        if revision_list[i].revision_number == rev:
            revision = revision_list.pop(i)
            break
    if revision is None and revision_list == []:
        flash(f"No revisions found for obsid = {obsid}.")
        return redirect(url_for('chkupdata.provide_obsidrev'))
    elif revision is None and revision_list != []:
        flash(f"Could not find obsid.rev = {obsidrev}. Returning most recent revision instead.")
        revision = revision_list.pop(-1)
    other_rev = {f"{r.obsid}.{r.revision_number:>03}" : url_for('chkupdata.index',obsidrev= f"{r.obsid}.{r.revision_number:>03}") for r in revision_list}
    #
    # --- Fetch state information of this obsid
    #
    ocat_data = rod.read_ocat_data(obsid)

    originals = revision.original
    if revision.kind == 'norm':
        requests = revision.request
    else:
        requests = [] #: If revision wasn't norm this would be the fetch result regardless, but assigning it on the python side is quicker
    org_dict = {}
    for org in originals:
        org_dict[org.parameter.name] = json.loads(org.value)
    req_dict = {}
    for req in requests:
        req_dict[req.parameter.name] = json.loads(req.value)

    #: Add unchanging ocat information from the ocat to the original state record so that the display indicates information without indicating an impossible change
    compare_but_uneditable = {}
    for param in _PARAM_SELECTIONS['compare_but_uneditable']:
        compare_but_uneditable[param] = ocat_data.get(param)
    org_dict.update(compare_but_uneditable)

    return render_template('chkupdata/index.html',
                           revision = revision,
                           ocat_data = ocat_data,
                           org_dict = org_dict,
                           req_dict = req_dict,
                           other_rev = other_rev,
                           _LABELS = _LABELS,
                           _PARAM_SELECTIONS = _PARAM_SELECTIONS
                           )

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def provide_obsidrev():
    obsidrev_form = ObsidRevForm(request.form)
    if request.method == "POST" and obsidrev_form.is_submitted():
        return redirect(url_for('chkupdata.index', obsidrev = obsidrev_form.obsidrev.data))
    return render_template('chkupdata/provide_obsidrev.html',
                           obsidrev_form = obsidrev_form
                           )
