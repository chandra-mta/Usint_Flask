"""
**ocatdatapage/routes.py**: Render the Ocat Data Page

:Author: W. Aaron (william.aaron@cfa.harvard.edu)
:Last Updated: Mar 13, 2025

"""

import os
import numpy
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from flask              import current_app, render_template, request
from cus_app.ocatdatapage   import bp
from cus_app.ocatdatapage.forms import OcatParamForm
import cus_app.supple.read_ocat_data         as rod

@bp.route('/',              methods=['GET', 'POST'])
@bp.route('/<obsid>',       methods=['GET', 'POST'])
@bp.route('/index/<obsid>', methods=['GET', 'POST'])
def index(obsid=None):
    #
    #--- Render Ocat Data In A WTForm
    #
    ocat_data = rod.read_ocat_data(obsid)
    form     = OcatParamForm(data = ocat_data)
    if form.validate_on_submit():
        print("entered valid on submit")
        form_obsid = form.obsid.data
        targname = form.targname.data
        return f"{form_obsid} and {targname}"
    if request.method == 'POST':
        print("entered via POST check")
        form_obsid = form.obsid.data
        targname = form.targname.data
        return f"{form_obsid} and {targname}"

    return render_template('ocatdatapage/index.html', form=form)

