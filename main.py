#!/usr/bin/env python3

##############################
#            init            #
##############################

from bottle import route, run, template, static_file, post, request, response
import os
import json
import re

# functions.py script
import functions as f

# constant
HOME_DIR = os.path.expanduser('~')


# load configuration
# TODO: temp
extension_preferences = {'framapad': 'csv', 'etherpad': 'txt'}

# import urls into database
#TODO

##############################
#        static files        #
##############################
# allow the web server to serve static files

# folder static
@route('/static/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root='./static')

@route('/add_backup/static/<filepath:path>')
def server_static1(filepath):
    return static_file(filepath, root='./static')

@route('/services/static/<filepath:path>')
def server_static1(filepath):
    return static_file(filepath, root='./static')

# boostrap's files (standard and custom ones)
@route('/bootstrap/<filepath:path>')
def server_bootsrap(filepath):
    return static_file(filepath, root='./bootstrap')

@route('/add_backup/bootstrap/<filepath:path>')
def server_bootsrap1(filepath):
    return static_file(filepath, root='./bootstrap')

@route('/services/bootstrap/<filepath:path>')
def server_bootsrap1(filepath):
    return static_file(filepath, root='./bootstrap')


##############################
#        define routes       #
##############################
# bind locations to templates

@route('/')
def welcome_page():
    return template('welcome', no_config = f.no_config(), no_websites = f.no_websites(), bar_list_services = f.get_list_services_html())

@route('/search')
def search_page():
    return template('search', bar_list_services = f.get_list_services_html())

@route('/settings')
def settings_page():
    return template('settings', bar_list_services = f.get_list_services_html())

@route('/add_service')
def add_service():
    return template('add_service', bar_list_services = f.get_list_services_html(), message = '')

@post('/add_service') # or @route('/login', method='POST')
def add_service_post():
    service_name = request.forms.get('service_name')
    service_url = request.forms.get('service_url')
    service_url = re.sub(r'^https?:\/\/', '',service_url) # remove http or https
    software_type = request.forms.get('software_type')
    try:
        f.add_service(service_name, service_url, software_type)
        return template('add_service', bar_list_services = f.get_list_services_html(), message = '<div class="alert alert-success" role="alert">Your service was correctly added.</div>')
    except:
        return template('add_service', bar_list_services = f.get_list_services_html(), message = '<div class="alert alert-danger" role="alert">FAILED! Your service was not added.</div>')


@route('/help')
def help_page():
    return template('help', bar_list_services = f.get_list_services_html())

@route('/about')
def about_page():
    return template('about', bar_list_services = f.get_list_services_html())

@route('/services')
def list_services_page():
    return template('list_services', bar_list_services = f.get_list_services_html(), list_services = f.get_list_services_group_html())

@route('/services/<name:re:.+>')
def services_page(name):
    return template('services', service = name, bar_list_services = f.get_list_services_html(name), list_content = f.get_list_content_html(name), message = '')

@post('/services/<name:re:.+>')
def update_content_post(name):
    service_name = name
    url = request.forms.get('url')
    content_name = request.forms.get('content_name')
    description = request.forms.get('description')
    save_method = request.forms.get('save')
    if content_name != None: # update the name
        f.update_content_name(url, content_name)
    elif description != None: # update the description
        f.update_content_description(url, description)
    elif save_method != None: # update the save_method
        f.update_content_save_method(url, save_method)
    else:
        return "Sorry, wrong arguments."
    return content_name


@route('/add_backup/<idc:int>')
def services_page(idc):
    message = f.show_html_backup_one_content_now(idc, extension_preferences) # backup and returns an html message
    return template('add_backup', bar_list_services = f.get_list_services_html(), message = message)

@route('/download/<idc:int>/<date:re:.+>')
def download_backup(idc, date):
    content = f.retrieve_one_backup(idc, date)
    software_type = f.retrieve_software_type_from_idc(idc)
    filename = "backup_"+str(idc)+"."+extension_preferences[software_type]
    with open('./temp/'+filename, "w") as f_temp:
        f_temp.write(content)
    return static_file(filename, root='./temp', download=filename)


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
