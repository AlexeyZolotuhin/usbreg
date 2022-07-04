# -*- coding: utf-8 -*-
from flask import render_template, make_response, redirect, url_for, request
from app.main import bp


@bp.route('/')
@bp.route('/index')
def index():
    username = request.cookies.get('username')
    return render_template('index.html', title="Приветствие", username=username)