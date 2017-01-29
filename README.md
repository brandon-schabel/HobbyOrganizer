# HobbyOrganizer
A Flask application made for organizing your hobby. I am personally using it to organize my electronic components and tools.

to install all the required python packages, in the command line run "pip install -r requirements.txt"

if you have added packages to the projects create a new requirements.txt "pip freeze > requirements.txt"

the config.ini should have all the configuration options to get you running, you're going to need a user database, and a hobby database

server_url: is the url to your database, if you go to mlab.com create a new database, it should be pretty self explanatory

server_port: is the port to the database

db_server_name: name of your database

db_user: username that you created for your database

db_pass: password you created for your database

hobby_coll: the collection you'll be storing your hobby entries

user_coll: the collection you'll be storing users

sec_key: set as a string to whatever you want

Here is an example config.ini
;https://wiki.python.org/moin/ConfigParserExamples

[database_config]

server_url: ds1000000101.mlab.com

server_port: 10000

db_server_name: hobby_organizer

db_user: admin

db_pass: admin

hobby_coll: hobby_coll

user_coll: user_coll

sec_key: 'whatever_you_want_it_to_be_123456789'