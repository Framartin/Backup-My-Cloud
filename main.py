#!/usr/bin/env python3

##############################
#            init            #
##############################

from bottle import route, run, template, static_file
import os
import json

# functions.py script
import functions as f

# constant
HOME_DIR = os.path.expanduser('~')



##############################
#        static files        #
##############################
# allow the web server to serve static files

# folder static
@route('/static/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root='./static')

# boostrap's files (standard and custom ones)
@route('/bootstrap/<filepath:path>')
def server_bootsrap(filepath):
    return static_file(filepath, root='./bootstrap')


##############################
#        define routes       #
##############################
# bind locations to templates

@route('/')
def welcome_page():
    return template('welcome', no_config = f.no_config(), no_websites = f.no_websites())

@route('/search')
def search_page():
    return template('search')

@route('/settings')
def settings_page():
    return template('settings')

@route('/help')
def help_page():
    return template('help')

@route('/about')
def about_page():
    return template('about')

# doesn't work
#@route('/quit')
#def quit_page():
#    exit()

##############################
#         web server         #
##############################
# run the local web server

# Uncomment for debug
run(host='localhost', port=8080, debug=True)

#run(host='localhost', port=8080)
