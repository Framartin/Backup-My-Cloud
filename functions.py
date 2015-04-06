
##########################
#      init functions    #
##########################

import os.path

# if no config exists (first use)
def no_config(): # return True is no config exists
    return not os.path.isfile('config/config.json')

# if no websites are saved
def no_websites():
    return not os.path.isfile('config/websites.json')





