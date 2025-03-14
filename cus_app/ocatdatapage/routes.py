"""
**ocatdatapage/routes.py**: Render the Ocat Data Page

:Author: W. Aaron (william.aaron@cfa.harvard.edu)
:Last Updated: Mar 13, 2025

"""

import os
import numpy
from datetime import datetime
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from wtforms.validators import ValidationError

from flask import current_app, render_template, request
from cus_app.ocatdatapage import bp
from cus_app.ocatdatapage.forms import OcatParamForm
import cus_app.supple.read_ocat_data as rod

_OCAT_DATETIME_FORMAT = "%b %d %Y %I:%M%p"  #: NOTE Ocat dates are recorded without a leading zero. While datetime can process these dates, it never prints without a leading zero

_FORM_BY_CATEGORY = {
    "gen_param": [
        "targname",
        "instrument",
        "grating",
        "type",
        "ra_hms",
        "dec_dms",
        "y_det_offset",
        "z_det_offset",
        "trans_offset",
        "focus_offset",
        "uninterrupt",
        "extend_src",
        "obj_flag",
        "object",
        "photometry_flag",
        "vmagnitude",
        "est_cnt_rate",
        "forder_cnt_rate",
    ],
    "dither_param": [
        "dither_flag",
    ],
    "time_param": ["time_ordr", "window_constraint", "tstart", "tstop"],
}


def verbose_validate_on_submit(form):
    if form.is_submitted():
        is_valid = True
        for field in form:
            print(f"Checking validators for {field.name}")
            for validator in field.validators:
                try:
                    validator(form, field)
                except ValidationError as e:
                    is_valid = False
                    print(
                        f"Validation failed for {field.name} with {validator.__class__.__name__}: {str(e)}"
                    )
            if field.type == "FormField":
                for subfield in field:
                    print(f"Checking validators for {subfield.name}:")
                    for validator in subfield.validators:
                        try:
                            validator(form, subfield)
                            print(f"  {validator.__class__.__name__}: Passed")
                        except ValidationError as e:
                            print(
                                f"  {validator.__class__.__name__}: Failed - {str(e)}"
                            )
        return is_valid
    return False


@bp.route("/", methods=["GET", "POST"])
@bp.route("/<obsid>", methods=["GET", "POST"])
@bp.route("/index/<obsid>", methods=["GET", "POST"])
def index(obsid=None):
    #
    # --- Render Ocat Data In A WTForm
    #
    if not request.form:
        ocat_data = rod.read_ocat_data(obsid)
        form_starting_values = format_for_form(ocat_data)
        print(form_starting_values)
        form = OcatParamForm(data=form_starting_values)
    else:
        form = OcatParamForm(request.form)
    # if form.validate_on_submit():
    if request.method == "POST":
        if verbose_validate_on_submit(form):
            print("Form is valid")
        else:
            print("Form is not valid")
        line = ""
        for key in form:
            line += f"<p>{key.label} : {key.data}</p>"
        return line
    return render_template("ocatdatapage/index.html", form=form, ocat_data=ocat_data)


def format_for_form(ocat_data):
    form = {}
    for category, parameter_list in _FORM_BY_CATEGORY.items():
        form[category] = {}
        for param in parameter_list:
            form[category][param] = ocat_data.get(param)
    #
    # --- Adjustments for Form
    #
    tstart = form["time_param"].get("tstart")
    if tstart is not None:
        form["time_param"]["tstart"] = [
            datetime.strptime(x, _OCAT_DATETIME_FORMAT) for x in tstart
        ]

    tstop = form["time_param"].get("tstop")
    if tstop is not None:
        form["time_param"]["tstop"] = [
            datetime.strptime(x, _OCAT_DATETIME_FORMAT) for x in tstop
        ]

    return form
