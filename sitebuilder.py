#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, locale

from flask import Flask, render_template, url_for, make_response, request
from flask_flatpages import FlatPages, pygments_style_defs
from flask_frozen import Freezer
from werkzeug import SharedDataMiddleware
from werkzeug.contrib.atom import AtomFeed
from BeautifulSoup import BeautifulSoup

locale.setlocale(locale.LC_ALL, ('fr_FR', 'UTF-8'))

DEBUG = True
FLATPAGES_AUTO_RELOAD = DEBUG
FLATPAGES_EXTENSION = '.md'
FREEZER_BASE_URL = 'http://www.deltalima.net'
FREEZER_DESTINATION = 'build'

if 'demo' in sys.argv:
    FREEZER_BASE_URL = 'http://demo.deltalima.net/www'
    FREEZER_DESTINATION = 'build/www'


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

@app.template_filter()
def summarize(html):
    if '<!-- BODY -->' in html:
        html = html[:html.index('<!-- BODY -->')]
        return unicode(BeautifulSoup(html))
    else:
        return unicode(BeautifulSoup(html).p)

#
# Helpers
#
def generate_feed(title, articles):
    feed = AtomFeed(title,
                    feed_url=request.url,
                    url=request.url_root,
                    author='Laurent Meunier',
                    icon=url_for('static', filename='favicon.ico'))

    articles = sorted(articles, reverse=True, key=lambda p: p.meta['published_date'])
    for article in articles:
        feed.add(article.meta['title'],
                 unicode(article.html),
                 content_type='html',
                 author='Laurent Meunier',
                 url=url_for('page', path=article.path, _external=True),
                 updated=article.meta['published_date'])
    return feed.get_response()

#
# Routes
#
@app.route('/pygments.css')
def pygments_css():
    return pygments_style_defs(), 200, {'Content-Type': 'text/css'}

@app.route('/sitemap.xml')
def sitemap():
    urls = []

    # all pages
    for page in pages:
        path = page.path
        if path == 'index':
            path = None
        urls.append(url_for('page', path=path, _external=True))

    # all tags
    tags = []
    for page in pages:
        if 'tags' in page.meta:
            tags += page.meta['tags']
    tags = list(set(tags))
    for tag in tags:
        urls.append(url_for('show_tag', tag=tag, _external=True))

    response = make_response(render_template('sitemap.xml', urls=urls))
    response.headers['Content-type'] = 'text/xml; charset=utf-8'
    return response

@app.route('/feed/all.atom')
def feed_all():
    title = 'deltalima.net - Recent Articles'
    articles = (p for p in pages if 'published_date' in p.meta)
    return generate_feed(title, articles)

@app.route('/feed/tag/<string:tag>.atom')
def feed_tag(tag):
    title = "deltalima.net - Recent Articles for tag '" + tag + "'"
    articles = (p for p in pages if 'published_date' in p.meta and tag in p.meta.get('tags', []))
    return generate_feed(title, articles)

@app.route('/tag/<string:tag>/')
def show_tag(tag):
    articles = (p for p in pages if tag in p.meta.get('tags', []))
    articles = sorted(articles, reverse=True, key=lambda p: p.meta['published_date'])
    page = {
        'title': tag,
    }
    return render_template('tag.html', tag=tag, page=page, articles=articles)

@app.route('/', defaults={'path': 'index'})
@app.route('/<path:path>/')
def page(path):
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
    yield '/sitemap.xml'
    yield '/favicon.ico'

#
# Main
#
if __name__ == '__main__':
    if 'build' in sys.argv:
        freezer.freeze()
    elif 'serve' in sys.argv:
        freezer.serve()
    elif 'run' in sys.argv:
        freezer.run()
    else:
        app.run(host='0.0.0.0', port=8000)
