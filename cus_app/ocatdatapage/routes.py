"""
**ocatdatapage/routes.py**: Render the Ocat Data Page

:Author: W. Aaron (william.aaron@cfa.harvard.edu)
:Last Updated: Mar 13, 2025

"""

from multiprocessing import synchronize
import os
import numpy
import copy
from datetime import datetime
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from wtforms.validators import ValidationError

from flask import current_app, render_template, request
from cus_app.ocatdatapage import bp
from cus_app.ocatdatapage.forms import OcatParamForm
import cus_app.supple.read_ocat_data as rod
import cus_app.ocatdatapage.format_ocat_data as fod


@bp.route("/", methods=["GET", "POST"])
@bp.route("/<obsid>", methods=["GET", "POST"])
@bp.route("/index/<obsid>", methods=["GET", "POST"])
def index(obsid=None):
    #
    # --- Render Ocat Data In A WTForm
    #
    ocat_data = rod.read_ocat_data(obsid)
    form_dict = fod.format_for_form(ocat_data) #: Formats information into form and provides additional form-specific parameters
    form = OcatParamForm(request.form,data=form_dict)
    print(request.form)
    if request.method == 'POST' and form.is_submitted():
        #: Processing a POSTed form
        if form.open_dither.data:
            #: Refresh the page with the dither entries as initialized by **format_for_form()**
            form.dither_param.dither_flag.data = 'Y'
        if form.refresh.data:
            #: Process the changes submitted to the form for how they would update the form and param_dict objects
            form = fod.synchronize_values(form)
    return render_template("ocatdatapage/index.html", form=form)
