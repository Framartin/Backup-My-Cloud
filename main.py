#!/usr/bin/env python3

##############################
#            init            #
##############################

from bottle import route, run, template, static_file

# functions.py script
import functions as f


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

@route('/')
def welcome():
    return template('welcome', no_config = f.no_config(), no_websites = f.no_websites())


@route('/settings')
def settings():
    return template('settings')

# run the local web server

# Uncomment for debug
#run(host='localhost', port=8080, debug=True)

run(host='localhost', port=8080)
