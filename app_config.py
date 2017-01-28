import configparser
from pymongo import MongoClient

def ConfigSectionMap(section):
    config = configparser.ConfigParser()
    config.read("./config.ini")
    dict1 = {}
    #sections are defined in config.ini and are listed as [NameHere]
    options = config.options(section)
    for option in options:
        try:
            dict1[option] = config.get(section,option)
            if dict1[option] == -1:
                DebugPrint("Skip: %s" % option)
        except:
            print("Exception on %s!" % option)
            dict1[option] = None
    return dict1

config = ConfigSectionMap('database_config')

client = MongoClient(config['server_url'], int(config['server_port']))
# connecting to our mlab database
db = client[config['db_server_name']]
db.authenticate(config['db_user'], config['db_pass'])

hobby_coll = db[config['hobby_coll']]
user_coll = db[config['user_coll']]

def update_sec_key():
    return config['sec_key']
