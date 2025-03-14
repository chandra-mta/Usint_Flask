"""
**ocatdatapage/routes.py**: Render the Ocat Data Page

:Author: W. Aaron (william.aaron@cfa.harvard.edu)
:Last Updated: Mar 13, 2025

"""

import os
import numpy
from datetime import datetime
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from flask import current_app, render_template, request
from cus_app.ocatdatapage import bp
from cus_app.ocatdatapage.forms import OcatParamForm
import cus_app.supple.read_ocat_data as rod

_OCAT_DATETIME_FORMAT = "%b %d %Y %I:%M%p"  #: NOTE Ocat dates are recorded without a leading zero. While datetime can process these dates, it never prints without a leading zero


@bp.route("/", methods=["GET", "POST"])
@bp.route("/<obsid>", methods=["GET", "POST"])
@bp.route("/index/<obsid>", methods=["GET", "POST"])
def index(obsid=None):
    #
    # --- Render Ocat Data In A WTForm
    #
    ocat_data = rod.read_ocat_data(obsid)
    #: TODO Write a separation step in which directly ocat_data is formatted into selection specifically used by the form.
    form_starting_values = {
        "gen_param": {
            "obsid": ocat_data.get("osbid"),
            "targname": ocat_data.get("targname"),
        },
        "dither_param": {"dither_flag": ocat_data.get("dither_flag")},
        "time_param": {
            "time_ordr": ocat_data.get("time_ordr"),
            "window_constraint": ocat_data.get("window_constraint"),
            "tstart": [datetime.strptime(x,_OCAT_DATETIME_FORMAT) for x in ocat_data.get('tstart')],
            "tstop": [datetime.strptime(x,_OCAT_DATETIME_FORMAT) for x in ocat_data.get('tstop')]
        },
    }
    form = OcatParamForm(request.form, data=form_starting_values)
    #if form.validate_on_submit():
    if request.method == 'POST' and form.submit.submit:
        line = ""
        for key in form:
            line += f"<p>{key.label} : {key.data}</p>"
        return line
    return render_template("ocatdatapage/index.html", form=form, ocat_data=ocat_data)
