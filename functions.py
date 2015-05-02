
##########################
#     init functions     #
##########################

# if no config exists (first use)
def no_config(): # return True is no config exists
    return not os.path.isfile('config/config.json')

# if no websites are saved
def no_websites():
    return not os.path.isfile('config/websites.json')


##########################
#   create/load config   #
##########################




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

def download_from_content(url, software_type, extension = "html"):
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
    file = download(url)

# extract framapad name and description
def extract_framapad_description(url):
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
                           name TEXT,
                           url TEXT NOT NULL,
                           software_type TEXT,
                           CONSTRAINT url_service UNIQUE (url)
                           )''')
    c.execute('''CREATE TABLE IF NOT EXISTS content(
                           idC INTEGER PRIMARY KEY,
                           url TEXT NOT NULL,
                           auto_DL BOOL NOT NULL,
                           name TEXT,
                           description TEXT,
                           blacklist BOOL,
                           CONSTRAINT url_content UNIQUE (url)
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

def add_content(url, autodl = False, name = None, description = None, blacklist = False):
    conn = sqlite3.connect('database.sqlite')
    c = conn.cursor()
    line = (url, autodl, name, description, blacklist)
    c.execute("INSERT INTO content VALUES (NULL, ?,?,?,?,?)", line)
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

### Retrieve a specific backup
def retrieve_one_backup(url, date):
    conn = sqlite3.connect('database.sqlite')
    c = conn.cursor()
    line = (url, date)
    c.execute('''SELECT content
                 FROM backup
                 WHERE idc = (SELECT idC FROM content WHERE url = ?)
                    AND date = ? ''', line)
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

# retrieve all url of one service


def retrieve_content_software(software_type):
    conn = sqlite3.connect('database.sqlite')
    urls = conn.execute('''SELECT * 
                            FROM moz_places
                            WHERE url {} ;'''.format(condition)).fetchall()
    conn.close()
    urls = [x[0] for x in urls] # list of 1-uple to list
    return urls

##########################
#          #
##########################

#load_file


#list_files



##########################
#     search a query     #
##########################




