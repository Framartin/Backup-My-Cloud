
##########################
#     init functions     #
##########################

# if no config exists (first use)
def no_config(): # return True is no config exists
    return not os.path.isfile('config.json')



##########################
#   create/load config   #
##########################
import json

# load the config
# if failed, create it
def load_config():
    if no_config():
        config = {'format':{'etherpad':'html', 'framadate':'csv'}}
        with open ("config.json", "w") as f: 
            json.dump(config, f)
    else:
        with open ("config.json", "r") as f: 
            config = json.load(f)
    return config

# saved config
def save_config(config):
    with open ("config.json", "w") as f: 
        json.dump(config, f)


##########################
#   webbrowser profiles  #
##########################

import platform
import sqlite3
import re
from glob import glob
import os.path
# we support multiple profiles

# extract Firefox profiles names
def path_line(row):
    p = re.compile('Path=(.+)')
    if re.search("Path=", row):
        p.match(row).group(1)

# FF profiles names from profiles.ini
def get_firefox_profiles(firefox_dir):
    if not os.path.exists(firefox_dir):
        return []
    if not os.path.isfile(firefox_dir+"profiles.ini"): # old FF version
        return glob(firefox_dir+"*.[dD]efault/")
    firefox_profiles = []
    p = re.compile('Path=(.+)')
    with open (firefox_dir+"profiles.ini", "r") as f:
        for row in f.readlines():
            if re.search("Path=", row):
                firefox_profiles = firefox_profiles + [firefox_dir+p.match(row).group(1)+'/']
    return firefox_profiles

def get_profiles(os_type):
    HOME_DIR = os.path.expanduser('~')
    if os_type == "Linux":
        firefox_dir = glob(HOME_DIR + "/.mozilla/firefox/")
        if firefox_dir != []:
            firefox_profiles = get_firefox_profiles(firefox_dir[0])
        else:
            firefox_profiles = []
        chrome_profiles = glob(HOME_DIR + "/.config/google-chrome/Default/")
        chromium_profiles = glob(HOME_DIR + "/.config/chromium/Default/")
    elif os_type == "Windows":
        firefox_profiles = get_firefox_profiles(os.getenv('APPDATA') + "\Mozilla\Firefox\Profiles\\") #glob(os.getenv('APPDATA') + "\Mozilla\Firefox\Profiles\*.default\\")
        if platform.release() == "XP":
            chrome_profiles = glob("C:\Documents and Settings\{}\Local Settings\Application Data\Google\Chrome\\User Data\Default\\".format(os.getenv("USERNAME")))
            chromium_profiles = glob("C:\Documents and Settings\{}\Local Settings\Application Data\Chromium\\User Data\Default\\".format(os.getenv("USERNAME")))
        else:
            chrome_profiles = glob("C:\\Users\{}\AppData\Local\Google\Chrome\\User Data\Default\\".format(os.getenv("USERNAME")))
            chromium_profiles = glob("C:\\Users\{}\AppData\Local\Chromium\\User Data\Default\\".format(os.getenv("USERNAME")))
    else:
        firefox_profiles = get_firefox_profiles(HOME_DIR + "/Library/Mozilla/.mozilla/firefox/")
        chrome_profiles = glob(HOME_DIR + "/Library/Application Support/Google/Chrome/Default/")
        chromium_profiles = glob(HOME_DIR + "/Library/Application Support/Chromium/Default/")
    return firefox_profiles, chrome_profiles, chromium_profiles


##########################
#      find content      #
##########################
import json

# FF history and bookmarks are both stored on a same table of one sqlite's database 
def retrieve_firefox_urls(profile, condition):
    conn = sqlite3.connect(profile + 'places.sqlite')
    urls = conn.execute('''SELECT DISTINCT RTRIM(url, '/')
                            FROM moz_places
                            WHERE url {} ;'''.format(condition)).fetchall()
    conn.close()
    urls = [x[0] for x in urls] # list of 1-uple to list
    return urls

# for Chrome bookmarks (JSON file)
def extract_nested_urls(bookmark):
    urls = []
    if isinstance(bookmark, dict):
        if 'children' in bookmark.keys():
            return extract_nested_urls(bookmark['children'])
        if 'url' in bookmark.keys():
            return [bookmark['url']]
        else:
            for x in bookmark.keys():
                urls = urls + extract_nested_urls(bookmark[x])
            return urls
            #return [extract_nested_urls(bookmark[x]) for x in bookmark.keys()]
    elif isinstance(bookmark, list):
        if bookmark == []: # one of the top dict (roots, synced or bookmark_bar) contains an empty list
            return []
        else:
            for x in bookmark:
                urls = urls + extract_nested_urls(x)
            return urls
    else:
        return urls

# extract chrome bookmarks from the JSON file
# example: reg_exp='.*framapad.*'
def retrieve_chrome_bookmarks(profile, reg_exp):
    with open (profile+"Bookmarks", "r") as f:
        bookmarks = json.load(f)
    # roots can countained sub-directories
    # locations of bookmarks : roots, synced, bookmark_bar
    urls = extract_nested_urls(bookmarks) # every bookmarks
    r = re.compile(reg_exp)
    urls_subset = list(filter(r.match, urls))
    return urls_subset

# Chrome history is on one sqlite database
def retrieve_chrome_urls(profile, condition):
    conn = sqlite3.connect(profile + 'History')
    urls = conn.execute('''SELECT DISTINCT url
                            FROM urls
                            WHERE url {} ;'''.format(condition)).fetchall()
    conn.close()
    urls = [x[0] for x in urls] # list of 1-uple to list
    return urls

#

# associate a type of software and a instance with a condition 
def get_conditions(software_type, url_instance):
    if software_type == "etherpad":
        condition_sql, condition_reg_exp = 'LIKE "%{}/p/%" AND url NOT LIKE "%/timeslider%"'.format(url_instance), '.*{}\/p\/.+(?<!\/timeslider)$'.format(url_instance)
# LIKE "%framapad.org/p/%" AND url NOT LIKE "%/timeslider%"
# .*framapad.org/p/.+(?<!/timeslider)$
# does not match history pages of framapad
    else:
        condition_sql, condition_reg_exp = 'LIKE "%{}/%"'.format(url_instance), '.*{}/.+'.format(url_instance)
    return condition_sql, condition_reg_exp


def url_from_browsers(software_type, url_instance):
    os_type = platform.system()
    firefox_profiles, chrome_profiles, chromium_profiles = get_profiles(os_type)
    # if one broswer is not installed returns []
    condition_sql, condition_reg_exp = get_conditions(software_type, url_instance)
    urls = []
    for profile in firefox_profiles: # ok if firefox_profiles is empty
        urls = urls + retrieve_firefox_urls(profile, condition_sql)
    for profile in chrome_profiles: # ok if chrome_profiles is empty
        urls = urls + retrieve_chrome_bookmarks(profile, condition_reg_exp)
        urls = urls + retrieve_chrome_urls(profile, condition_sql)
    for profile in chromium_profiles: # ok if chromium_profiles is empty
        urls = urls + retrieve_chrome_bookmarks(profile, condition_reg_exp)
        urls = urls + retrieve_chrome_urls(profile, condition_sql)
    
    # special additionnal conditions
    # opensondage : we match admin pages and just need the first part of the url
    # sondage id = 16 caracters ; cf the sourcecode : https://git.framasoft.org/framasoft/framadate/blob/master/creation_sondage.php line 64
    if software_type == "framadate":
        reg_exp_1 = '^(.+{}'.format(url_instance)+"\/.{16}).+\/admin"
        reg_exp_2 = r'\1'
        urls = [re.sub(reg_exp_1, reg_exp_2, x) for x in urls]
    elif software_type == "etherpad":
        urls = [re.sub(r'\/export\/.*$', '', x) for x in urls] # remove export to some url
    urls = list(set(urls)) # get unique values
    return urls

def a_not_in_b(a, b):
    return a not in b

# add the url to database (only urls not already present in database)
# using table service in DB
def url_to_database():
    registred_urls = retrieve_all_urls()
    services = retrieve_services_url_and_software_type() # returns list of tuples ('framapad.org', 'etherpad')
    for x in services:
        urls = url_from_browsers(software_type = x[1], url_instance = x[0])
        urls_not_in_database = [x for x in urls if x not in registred_urls] # filter urls
        for url in urls_not_in_database:
            if x[1] == 'framadate':
                title, description = extract_framadate_description(url)
            else:
                title, description = None, None
            add_content(url, service_url = x[0], autodl = False, name = title, description = description, blacklist = False)



##########################
#     download files     #
##########################

# warning: might be depreciated
# cf: http://stackoverflow.com/questions/7243750/download-file-from-web-in-python-3

import urllib.request

def download(url):
    try:
        #urllib.request.urlretrieve(url, pathfile)
        return urllib.request.urlopen(url).read().decode('utf-8')
    except:
        return None


##########################
#    download content    #
##########################

# from a content name, create the url to download the right content

def download_from_content(url, software_type, extension):
    if software_type == "etherpad":
        if extension in ['txt', 'html', 'doc', 'pdf']:
            url = url + '/export/' + extension
        else:
            #"format not supported"
            return None
    elif software_type == "framadate": # only export in csv
        url = re.sub('\/(.{16})$', r'/exportcsv.php?numsondage=\1', url)
        # https://framadate.org/exportcsv.php?numsondage=315nqrkke4kkff7u
    else:
        return None
    return download(url)

# extract framadate name and description
def extract_framadate_description(url):
    page_html = download(url)
    title = re.search('<h3>(.+)</h3>', page_html).group(1)
    description = re.search('<p class="form-control-static well">(.+)</p>', page_html)
    if description != None:
        description = description.group(1)
    return title, description


##########################
#        database        #
##########################

### CREATE

import sqlite3

def create_database():
    conn = sqlite3.connect('database.sqlite')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS service(
                           idS INTEGER PRIMARY KEY,
                           name TEXT NOT NULL,
                           url TEXT NOT NULL,
                           software_type TEXT NOT NULL,
                           CONSTRAINT url_service UNIQUE (url),
                           CONSTRAINT name_service UNIQUE (name)
                           )''')
    c.execute('''CREATE TABLE IF NOT EXISTS content(
                           idC INTEGER PRIMARY KEY,
                           idS INTEGER NOT NULL,
                           url TEXT NOT NULL,
                           auto_DL BOOL NOT NULL,
                           name TEXT,
                           description TEXT,
                           blacklist BOOL,
                           CONSTRAINT url_content UNIQUE (url),
                           FOREIGN KEY(idS) REFERENCES service(idS)
                           )''')
    c.execute('''CREATE TABLE IF NOT EXISTS backup(
                           idC INTEGER,
                           date DATETIME NOT NULL,
                           content TEXT,
                           PRIMARY KEY (idC, date),
                           FOREIGN KEY(idC) REFERENCES content(idC)
                           )''')
    conn.commit()
    conn.close()

### ADD CONTENT

# add a new instance
def add_service(name, url, software_type):
    conn = sqlite3.connect('database.sqlite')
    c = conn.cursor()
    line = (name, url, software_type)
    c.execute("INSERT INTO service VALUES (NULL, ?,?,?)", line)
    conn.commit()
    conn.close()

def add_content(url, service_url, autodl = False, name = None, description = None, blacklist = False):
    conn = sqlite3.connect('database.sqlite')
    c = conn.cursor()
    line = (service_url, url, autodl, name, description, blacklist)
    c.execute('''INSERT INTO content VALUES (NULL, 
                  (SELECT idS FROM service WHERE url = ?),
                  ?,?,?,?,?)''', line)
    conn.commit()
    conn.close()

# insert a new backup content
def add_backup(url, content):
    conn = sqlite3.connect('database.sqlite')
    c = conn.cursor()
    line = (url, content)
    c.execute('''INSERT INTO backup VALUES (
                 (SELECT idC FROM content WHERE url = ?),
                 datetime('now'), ?)''', line)
    conn.commit()
    conn.close()

### RETRIVE CONTENT

# Retrieve a specific backup
def retrieve_one_backup(idc, date):
    conn = sqlite3.connect('database.sqlite')
    c = conn.cursor()
    line = (idc, date)
    c.execute('''SELECT content
                 FROM backup
                 WHERE idc = ? AND date = ? ''', line)
    content = c.fetchone()
    if content != None:
        content = content[0]
    conn.commit()
    conn.close()
    return content

# retrieve all backups of one url
def retrieve_backups_from_url(url):
    conn = sqlite3.connect('database.sqlite')
    c = conn.cursor()
    url = (url,)
    c.execute('''SELECT date
                 FROM backup
                 WHERE idc = (SELECT idC FROM content WHERE url = ?) ''', url)
    content = c.fetchall()
    if content != []:
        content = [x[0] for x in content]
    conn.commit()
    conn.close()
    return content

# retrieve all url
def retrieve_all_urls():
    conn = sqlite3.connect('database.sqlite')
    c = conn.cursor()
    c.execute('''SELECT url
                 FROM content''')
    content = c.fetchall()
    if content != []:
        content = [x[0] for x in content]
    conn.commit()
    conn.close()
    return content

# retrieve all url of one service not blacklisted
# service identified as its URL
def retrieve_urls_from_service(service_name):
    conn = sqlite3.connect('database.sqlite')
    c = conn.cursor()
    service_name = (service_name,)
    c.execute('''SELECT idc, url, auto_dl, name, description, blacklist
                 FROM content
                 WHERE ids = (SELECT idS FROM service WHERE name = ?) 
                    AND blacklist == 0 ''', service_name)
    content = c.fetchall()
    conn.commit()
    conn.close()
    return content # returns a tuples

# idem but with a list of urls
def retrieve_urls_caracteristics(urls): # urls is a list
    conn = sqlite3.connect('database.sqlite')
    c = conn.cursor()
    content = []
    for url in urls:
        url = (url,)
        c.execute('''SELECT idc, url, auto_dl, name, description, blacklist
                     FROM content
                     WHERE url == ? ''', url)
        content = content + [c.fetchone()]
    conn.close()
    return content # returns a tuples

# retrieve all blacklisted url (from all services)
def retrieve_blacklisted_url():
    conn = sqlite3.connect('database.sqlite')
    c = conn.cursor()
    c.execute('''SELECT idc, url, name, description
                 FROM content
                 WHERE blacklist == 1 ''')
    content = c.fetchall()
    conn.commit()
    conn.close()
    return content # returns a tuples

# services names
def retrieve_services_names():
    conn = sqlite3.connect('database.sqlite')
    c = conn.cursor()
    c.execute('''SELECT name
                 FROM service ''')
    content = c.fetchall()
    if content != []:
        content = [x[0] for x in content]
    conn.commit()
    conn.close()
    return content

# services names and software type
def retrieve_services_url_and_software_type():
    conn = sqlite3.connect('database.sqlite')
    c = conn.cursor()
    c.execute('''SELECT url, software_type
                 FROM service ''')
    content = c.fetchall()
    conn.commit()
    conn.close()
    return content

# content url from content idc
def retrieve_content_url_from_idc(idc):
    conn = sqlite3.connect('database.sqlite')
    c = conn.cursor()
    idc = (idc,)
    c.execute('''SELECT url
                 FROM content
                 WHERE idc == ? ''', idc)
    content = c.fetchone()
    if content != None:
        content = content[0]
    conn.commit()
    conn.close()
    return content

# software type from content idc
def retrieve_software_type_from_idc(idc):
    conn = sqlite3.connect('database.sqlite')
    c = conn.cursor()
    idc = (idc,)
    c.execute('''SELECT software_type
                 FROM service
                 WHERE ids == (SELECT ids FROM content WHERE idc = ?) ''', idc)
    content = c.fetchone()
    if content != None:
        content = content[0]
    conn.commit()
    conn.close()
    return content

##########################
#  templates functions   #
##########################

# for header.tpl
# list of services names for the left bar
# <li><a href="/service/framapad">Framapad</a></li>
# the actual page is highlighted 
# <li class="active"><a href="/">Home <span class="sr-only">(current)</span></a></li>
def get_list_services_html(current_page = None):
    services = retrieve_services_names()
    html_list = ''
    for x in services:
        if x == current_page: # highlight the list member
            html_list = html_list + '<li class="active"><a href="/services/'+ x +'">'+x+' <span class="sr-only">(current)</span></a></li>\n'
        else:
            html_list = html_list + '<li><a href="/services/'+ x +'">'+x+'</a></li>\n'
    return html_list

# for list_services.tpl
# <a href="#" class="list-group-item">Dapibus ac facilisis in</a>
def get_list_services_group_html():
    services = retrieve_services_names()
    html_list = ''
    for x in services:
        html_list = html_list + '<a href="/services/'+ x +'" class="list-group-item">'+x+' </a>\n'
    return html_list

# for services.tpl
# services/<name>
# if urls is directly provided do not used service_name
def get_list_content_html(service_name, message = None, urls = None):  # message [idc,'my message'] : put my message in the idC list
    if urls!= None:
        content = retrieve_urls_caracteristics(urls) # list of tuples : idc, url, auto_dl, name, description, blacklist
    else:
        content = retrieve_urls_from_service(service_name) # list of tuples : idc, url, auto_dl, name, description, blacklist
    list_html = ''
    # display message after a post request
    if message == None:
        url_message, message = '', ''
    else:
        url_message, message = message[0], message[1]
    for x in content:
        idc, url, auto_dl, name, description, blacklist = str(x[0]), x[1], str(x[2]), x[3], x[4], str(x[5])
        if name == None:
            name = 'Set a name'
        if description == None:
            description = 'Set a description'
        checked_autosave, checked_manualsave, checked_blacklist = '', '', ''
        active_autosave, active_manualsave, active_blacklist = '', '', ''
        if blacklist == '1':
            checked_blacklist = ' checked'
            active_blacklist = ' active'
        elif auto_dl == '1':
            checked_autosave = ' checked'
            active_autosave = ' active'
        elif auto_dl == '0':
            checked_manualsave = ' checked'
            active_manualsave = ' active'
        else:
            checked_autosave, checked_manualsave, checked_blacklist = '', '', ''
        # display message after a post request
        if url == url_message:
            message_html = message
        else:
            message_html = ''
        # retrieve saved backups for this content
        backups_dates = retrieve_backups_from_url(url)
        backups_list = ''
        for date in backups_dates:
            backups_list = backups_list + '    <li><a href="/download/'+idc+'/'+str(date)+'">'+str(date)+'</a></li>\n'
        list_html = list_html + '''
<a name="anchor_'''+idc+'''"></a>
<h4 class="sub-header">'''+url+'''</h4>
'''+message_html+'''
<!-- Update name -->

<form method="post" class="form-inline" action="#anchor_'''+idc+'''">
  <div class="form-group">
    <input name="url" type="text" class="hidden form-control" value="'''+url+'''" >
    <label for="name">Name</label>
    <input name="content_name" type="text" class="form-control" id="content_name" placeholder="'''+name+'''">
  </div>
  <button type="submit" class="btn btn-default">Enter</button>
</form>

<!-- Update description -->
<form method="post" class="form-inline" action="#anchor_'''+idc+'''">
  <div class="form-group">
    <input name="url" type="text" class="hidden form-control" value="'''+url+'''" >
    <label for="description">Description</label>
    <input name="description" type="text" class="form-control" id="name" placeholder="'''+description+'''">
  </div>
  <button type="submit" class="btn btn-default">Enter</button>
</form>

<!-- Update save method -->
<form class="form-horizontal" method="post" action="#anchor_'''+idc+'''">

<div class="radio">
  <input name="url" type="text" class="hidden form-control" value="'''+url+'''" >
  <div class="btn-group" data-toggle="buttons">
    <label onClick="this.form.submit();" class="btn btn-info'''+active_autosave+'''">
      <input type="radio" name="save" id="autosave" value="autosave" onClick="this.form.submit();"'''+checked_autosave+'''> Save automatically
    </label>
    <label onClick="this.form.submit();" class="btn btn-info'''+active_manualsave+'''">
      <input type="radio" name="save" id="manualsave" value="manualsave" onClick="this.form.submit();"'''+checked_manualsave+'''> Save manually
    </label>
    <label onClick="this.form.submit();" class="btn btn-default'''+active_blacklist+'''">
      <input type="radio" name="save" id="blacklist" value="blacklist" onClick="this.form.submit();"'''+checked_blacklist+'''> Don't save (blacklist it)
    </label>
  </div>
</div>

</form>

<!-- List of available backups -->
<p>
<div class="btn-group">
  <button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown" aria-expanded="false">
    Download a backup <span class="caret"></span>
  </button>
  <ul class="dropdown-menu" role="menu">
      <li><a href="#">Dates of backups</a></li>
      <li class="divider"></li>'''+backups_list+'''
  </ul>
</div>


<!-- Manual backup now -->
  <a class="btn btn-primary" href="/add_backup/'''+idc+'''" role="button">Backup Now</a> 
</p>
<hr>'''
    return list_html

# update the content caracteristics
def update_content_name(url, name):
    conn = sqlite3.connect('database.sqlite')
    c = conn.cursor()
    line = (name, url)
    c.execute('''UPDATE content SET name = ?
                 WHERE url = ? ''', line)
    conn.commit()
    conn.close()

def update_content_description(url, description):
    conn = sqlite3.connect('database.sqlite')
    c = conn.cursor()
    line = (description, url)
    c.execute('''UPDATE content SET description = ?
                 WHERE url = ? ''', line)
    conn.commit()
    conn.close()

# save : manualsave , autosave, blacklist
def update_content_save_method(url, save):
    conn = sqlite3.connect('database.sqlite')
    c = conn.cursor()
    if save == "blacklist":
        line = (True, False, url)
    elif save == "manualsave":
        line = (False, False, url)
    elif save == "autosave":
        line = (False, True, url)
    else:
        conn.close()
        return None
    c.execute('''UPDATE content SET blacklist = ?, auto_dl = ?
                 WHERE url = ? ''', line)
    conn.commit()
    conn.close()


# for add_backup/<idc:int>
def backup_one_content_now(idc, extension_preferences): # extension_preferences is a dict {'etherpad':'txt', 'framapad':'csv'}
    # retrieve content url
    url = retrieve_content_url_from_idc(idc)
    # get the export url
    software_type = retrieve_software_type_from_idc(idc)
    extension = extension_preferences[software_type]
    content = download_from_content(url, software_type, extension)
    if content == None:
        return None
    add_backup(url, content)
    return True

def show_html_backup_one_content_now(idc, extension_preferences):
    status = backup_one_content_now(idc, extension_preferences)
    if status == True:
        return '<div class="alert alert-success" role="alert">Successfully backup!</div>'
    return '<div class="alert alert-danger" role="alert">ERROR! Backup process failed.</div>'

##########################
#     search a query     #
##########################

# words to urls
def search_in_database(words):
    conn = sqlite3.connect('database.sqlite')
    c = conn.cursor()
    words = re.sub(' ', '%', words)
    words = "%"+str(words)+"%"
    words = (words,words,words)
    c.execute('''SELECT DISTINCT content.url
                 FROM content
                 INNER JOIN backup ON backup.idc = content.idc
                 WHERE content.name LIKE ?
                    OR content.description LIKE ? 
                    OR backup.content LIKE ? ''', words)
    content = c.fetchall()
    if content != []:
        content = [x[0] for x in content]
    conn.close()
    return content

# generate the html list
def search_list_content_html(words):
    urls = search_in_database(words)
    return get_list_content_html(None, message = None, urls = urls)


