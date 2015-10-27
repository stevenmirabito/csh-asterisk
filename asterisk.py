#!/usr/bin/python

"""
Example AGI script to connect Asterisk to CSH LDAP

You can call this script directly with AGI() in the Asterisk dialplan
"""

import os
import CSHLDAP
from time import strftime

"""
Configuration
"""

debug = True
log_file = 'csh-demo.log'

"""
End Configuration
"""

def log(message):
	if debug:
		with open(log_file, 'a+') as log:
			log.write('[' + strftime("%Y-%m-%d %H:%M:%S") + '] ' + message + '\n')

if __name__ == "__main__":
	log("Starting CSH Demo AGI script")

	log("Connecting to CSH LDAP")
	# Create a connection to CSH's LDAP server
	ldap = csh.CSHLDAP('smirabito', 'S^kK@#rUP@hCH6N^cmdETr7f', app = True)

	log("Attempting to read caller ID from AGI environment...")
	# Get the user's phone number from caller ID
	callerid_number = '902'
	log("Got caller id: " + callerid_number)

	log("Searching LDAP for phone number...")
	# Search LDAP for a member with this phone number
	search = ldap.search(phone_number=callerid_number)

	# Convert the response to a list of member objects
	search_results = ldap.memberObjects(search)

	# Only continue if we found a member
	if len(search_results) > 0:
		# Grab the first member object returned
		member = search_results[0]
		member_attr = member.fields()
	
		log("Found a member: " + str(member))

		# Figure out the member's active/on-floor status
		member_status = ''

		if member.isActive():
			member_status += 'active, '
		else:
			member_status += 'inactive, '
	
		if member.isOnFloor():
			member_status += 'on floor'
		else:
			member_status += 'off floor'

		# Construct the welcome message
		response = 'Hello ' + member.fullName() + '! According to my records, you are currently an ' + member_status + ' member, with ' + member_attr['drink_balance'] + ' drink credits.'

		log("Constructed welcome message: " + response)
		log("Sending result to Asterisk")

		print(response)

	# Regardless of what happens, log that we're done
	log("Done!")
