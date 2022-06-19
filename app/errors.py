from flask import render_template, url_for
from flask_login import current_user
from app import app, db

@app.errorhandler(404)
def not_found_error(error):
    return render_template(
        '404.html',
        title='NotFound',
        homething='Go Back',
        homelink=url_for('mainfeed'),
        entry_1='Profile',
        entry_1_link=url_for('userprofile', username=current_user.username)
    )

@app.errorhandler(500)
def not_found_error(error):
    return render_template(
        '500.html',
        title='Error',
        homething='Go Back',
        homelink=url_for('mainfeed'),
        entry_1='Profile',
        entry_1_link=url_for('userprofile', username=current_user.username)
    )