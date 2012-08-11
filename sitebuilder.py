#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, locale

from flask import Flask, render_template
from flask_flatpages import FlatPages
from flask_frozen import Freezer
from werkzeug import SharedDataMiddleware

locale.setlocale(locale.LC_ALL, ('fr_FR', 'UTF-8'))

DEBUG = True
FLATPAGES_AUTO_RELOAD = DEBUG
FLATPAGES_EXTENSION = '.md'
FREEZER_BASE_URL = ''
FREEZER_DESTINATION = 'build/' + FREEZER_BASE_URL

app = Flask(__name__)
app.config.from_object(__name__)
pages = FlatPages(app)
freezer = Freezer(app)

app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
    '/': os.path.join(os.path.dirname(__file__), 'static')
})


#
# Filters
#
@app.template_filter()
def dateformat(value, format=u'%H:%M / %d-%m-%Y'):
    if not value:
        return u''
    return unicode(value.strftime(format).decode('utf8'))

#
# Routes
#
@app.route('/tag/<tag>/')
def show_tag(tag):
    articles = (p for p in pages if tag in p.meta.get('tags', []))
    articles = sorted(articles, reverse=True, key=lambda p: p.meta['published_date'])
    page = {
        'title': tag,
    }
    return render_template('tag.html', tag=tag, page=page, articles=articles)

@app.route('/')
@app.route('/<path:path>/')
def page(path="index"):
    page = pages.get_or_404(path)
    layout = page.meta.get('layout', 'page') + '.html'

    articles = []
    if 'list_pages' in page.meta:
        path = page.meta['list_pages']
        articles = (p for p in pages if p.path.startswith(path + '/') and 'published_date' in p.meta)
        articles = sorted(articles, reverse=True, key=lambda p: p.meta['published_date'])

    return render_template(layout, page=page, articles=articles)


#
# URL generators
#
@freezer.register_generator
def url_generator():
    yield '/robots.txt'

#
# Main
#
if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == "build":
        freezer.freeze()
    elif len(sys.argv) > 1 and sys.argv[1] == "serve":
        freezer.serve()
    elif len(sys.argv) > 1 and sys.argv[1] == "run":
        freezer.run()
    else:
        app.run(host='0.0.0.0', port=8000)
