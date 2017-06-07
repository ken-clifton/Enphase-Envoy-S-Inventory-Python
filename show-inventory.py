envoy_ip = '192.168.1.254'  # <-- change to your envoy ip address
user = 'envoy'
passwd = '999999'           # <-- change to your envoy password

#--------------------------------------------------------------------------------------------------------------------------------------# 
# Name:               show-inventory-html.py
#
# Purpose:            Read Envoy inverter inventory data directly from the Envoy.  
#                           Data is displayed in a Web browser window.
#                           A temp file named: envoy-inventory.html is used for the display
#                           and may be deleted.
#                           Basic authentication is used to log into the envoy. 
#                           JSON data is parsed using the standard Python JSON module, and
#                           Python list and dictionary objects.
#
#  Notes:               The Envoy IP address can be entered in the top line of the program
#                            The Envoy username 'envoy' should not need to be changed!
#                            The password to log in locally to the envoy is the last 6 digits of the
#                                 envoy serial number -- unless changed.
#
# Requires:             Python Version 3.0 or later  (tested on version 3.5)
# Author:                Ken Clifton
# Web site:              http://www.kenclifton.com
# Tested on:            Linux and Windows
#
# Created:               4/25/2017
#--------------------------------------------------------------------------------------------------------------------------------------#

import datetime

def convertJsonDatetoPython( jsonDate ):
	# convert installed date from JSON seconds value to Python date format
	java_timestamp = jsonDate
	seconds = float(java_timestamp)
	python_date = datetime.datetime.fromtimestamp(seconds)
	return python_date
	# end of  convertJsonDatetoPython() function
	# -----------------------------------------------------------------
	
def returnPCUControlText(item):
	if item == "envoy.cond_flags.pcu_ctrl.alertactive":
		return "Alert Active"
	elif item == "envoy.cond_flags.pcu_ctrl.altpwrgenmode":
		return "Alternate Pwr Gen Mode"
	elif item == "envoy.cond_flags.pcu_ctrl.altvfsettings":
		return "Alt. Volt & Freq. Settings"
	elif item == "envoy.cond_flags.pcu_ctrl.badflashimage":
		return "Bad Flash Image"
	elif item == "envoy.cond_flags.pcu_ctrl.bricked":
		return "No Grid Profile"
	elif item == "envoy.cond_flags.pcu_ctrl.commandedreset":
		return "Commanded Reset"
	elif item == "envoy.cond_flags.pcu_ctrl.criticaltemperature":
		return "Critical Temperature"	
	elif item == "envoy.cond_flags.pcu_ctrl.dc-pwr-low":
		return "DC Power Too Low"
	elif item == "envoy.cond_flags.pcu_ctrl.iuplinkproblem":
		return "IUP Link Problem"
	elif item == "envoy.cond_flags.pcu_ctrl.manutestmode":
		return "In Manu Test Mode"
	elif item == "envoy.cond_flags.pcu_ctrl.nsync":
		return "Grid Perturbation Unsynchronized"
	elif item == "envoy.cond_flags.pcu_ctrl.overtemperature":
		return "Over Temperature"
	elif item == "envoy.cond_flags.pcu_ctrl.poweronreset":
		return "Power On Reset"
	elif item == "envoy.cond_flags.pcu_ctrl.pwrgenoffbycmd":
		return "Power Gen Off by Cmd"
	elif item == "envoy.cond_flags.pcu_ctrl.runningonac":
		return "Running on AC"
	elif item == "envoy.cond_flags.pcu_ctrl.tpmtest":
		return "Transient Grid Profile"
	elif item == "envoy.cond_flags.pcu_ctrl.unexpectedreset":
		return "Unexpected Reset"
	elif item == "envoy.cond_flags.pcu_ctrl.watchdogreset":
		return "Watch Dog Reset"
	elif item == "envoy.cond_flags.obs_strs.discovering":
		return "Discovering"
	elif item == "envoy.cond_flags.obs_strs.failure":
		return "Falure to report"
	elif item == "envoy.cond_flags.obs_strs.flasherror":
		return "Flash error"
	elif item == "envoy.cond_flags.obs_strs.notmonitored":
		return "Not monitored"
	elif item == "envoy.cond_flags.obs_strs.ok":
		return "Normal"
	elif item == "envoy.cond_flags.obs_strs.plmerror":
		return "PLM Error"
	elif item == "envoy.cond_flags.obs_strs.secmodeenterfailure":
		return "Secure Mode Enter Failure"
	elif item == "envoy.cond_flags.obs_strs.secmodeexitfailure":
		return "Secure Mode Exit Failure"
	elif item == "envoy.cond_flags.obs_strs.sleeping":
		return "Sleeping"		
	else:
		return item
		
def read_envoy_data( envoy_ip_addr, username, password ):
	# function read_envoy_data gets the json data from the envoy

	import urllib.request
	import json
	import socket
	import base64
	
	socket.setdefaulttimeout(30)

	inventoryTableString = '/inventory.json' 
	
	# build the full url to get the eventTable
	url = 'http://' + envoy_ip_addr + inventoryTableString
	
	# encode a username/password tuple into base 64, 
	# decode it back into ASCII, manually inject it 
	# into the request header, and then use urllib.  
	credentials = base64.b64encode("{0}:{1}".format(username, password).encode()).decode("ascii")
	headers = {'Authorization': "Basic " + credentials}
	request = urllib.request.Request(url=url, headers=headers)
	
	try:
		response = urllib.request.urlopen(request,  timeout=30)
	except urllib.error.URLError as error:
		print('Data was not retrieved because error: {}\nURL: {}'.format(error.reason, url) )
		quit()  # exit the script - some error happened
	except socket.timeout:
		print('Connection to {} timed out, '.format( url))
		quit()  # exit the script - cannot connect
	
	try:
		# Convert bytes to string type and string type to dict
		string = response.read().decode('utf-8')
	except urllib.error.URLError as error:
		print('Reading of data stopped because error:{}\nURL: {}'.format(error.reason, url) )
		response.close()  # close the connection on error
		quit()  # exit the script - some error happened
	except socket.timeout:
		print('Reading data at {} had a socket timeout getting inventory, '.format( url))
		response.close()  # close the connection on error
		quit()  # exit the script - read data timeout
		
	json_data = json.loads(string)
	
	#close the open response object
	#urllib.request.urlcleanup()
	response.close()
	return json_data
	# ----------------------------  end of function to read envoy data

def writeHTMLPage():
	# call function read event log data from the envoy
	data = read_envoy_data(envoy_ip, user, passwd )

	# get the first list element which is the PCU devices dictionary
	pcu_device_collection = data[0]

	# debugging to see the pcu device dictionary keys
	#print( pcu_device_collection['devices'][0].keys() )

	# get the individual devices from that dictionary
	devices = pcu_device_collection['devices']

	# each device item is a dictionary containing the keys:
	# 'device_status', 'installed', 'producing', 'img_load_date',
	# 'device_control', 'ptpn', 'serial_num', 'chaneid', 'communicating',
	# 'dev_type', 'created_date', 'part_num', 'admin_state', 'img_pnum_running',
	# 'last_rpt_date', 'operating', 'provisioned'

	# open inventory_json_data.txt for read and set the variable "inFileRef" to the opened file
	outFileRef = open("envoy-inventory.html","w")

	outFileRef.write("<html>" + "\n")
	outFileRef.write("<style>" + "\n")
	outFileRef.write("tr:hover {" + "\n")
	outFileRef.write("background-color: #ffa;" + "\n")
	outFileRef.write("}" + "\n")
	outFileRef.write("</style>" + "\n")
	outFileRef.write("<head>" + "\n")
	outFileRef.write("</head>" + "\n")
	outFileRef.write("<body>" + "\n")
	outFileRef.write("<table border='1'>" + "\n")

	# write the table headings
	outFileRef.write("<thead>" + "\n")
	outFileRef.write("<tr>" + "\n")
	outFileRef.write("<th>Serial Num</th>" + "\n")
	outFileRef.write("<th>Communicating</th>" + "\n")
	outFileRef.write("<th>Last Report</th>" + "\n")
	outFileRef.write("<th>Part No</th>" + "\n")
	outFileRef.write("<th>Image Running</th>" + "\n")
	outFileRef.write("<th>Img Load Date</th>" + "\n")
	outFileRef.write("<th>Device Status</th>" + "\n")
	outFileRef.write("<th>Device Control Flags</th>" + "\n")
	outFileRef.write("<th>Installed Date</th>" + "\n")
	outFileRef.write("</tr>" + "\n")
	outFileRef.write("</thead>" + "\n")
	# end of table headings

	outFileRef.write("<tbody>" + "\n")

	# loop through each device printing information
	for device in devices:

		# debugging
		#print(device)

		# convert last report date from JSON seconds value to Python date format
		last_report_date = convertJsonDatetoPython(device['last_rpt_date'])

		# convert last report date from JSON seconds value to Python date format
		image_load_date = convertJsonDatetoPython(device['img_load_date'])

		# convert installed date from JSON seconds value to Python date format
		installed_date = convertJsonDatetoPython(device['installed'])
		
		# write the inventory data to table rows.
		outFileRef.write("<tr>" + "\n")
		outFileRef.write("<td>" + str(device['serial_num']) + "</td>" + "\n" )
		outFileRef.write("<td>" + str(device['communicating']) + "</td>" + "\n" )
		outFileRef.write("<td>" + str(last_report_date) + "</td>" + "\n" )
		outFileRef.write("<td>" + str(device['ptpn']) + "</td>" + "\n" )
		outFileRef.write("<td>" + str(device['img_pnum_running']) + "</td>" + "\n" )
		outFileRef.write("<td>" + image_load_date.strftime('%Y-%m-%d') + "</td>" + "\n" )
		
		# the following code handles the multiple device status possibility
		if str(device['device_status'][0]) == "envoy.global.ok":
			outFileRef.write("<td>" + "Global OK" + "</td>" + "\n" )
		else:  # otherwise write out all the device conditions present
			outFileRef.write("<td>")
			for item in device['device_status']:
				outFileRef.write(str(returnPCUControlText(item)) + "<br>" + "\n")
			outFileRef.write("</td>" + "\n")
		
		# the following code handles the multiple device control flags possibility
		outFileRef.write("<td>")
		for item in device['device_control']:
			if str(item) == "{'gficlearset': False}":  
				outFileRef.write("GFIClearSet: False")
			else:
				outFileRef.write(str(item) + "<br>" + "\n" )
		outFileRef.write("</td>" + "\n")
		
		outFileRef.write("<td>" +installed_date.strftime('%Y-%m-%d') + "</td>" + "\n" )
		outFileRef.write("</tr>" + "\n")

	# write out the end of the table and the end of the html page    
	outFileRef.write("</tbody>" + "\n")
	outFileRef.write("</table>" + "\n")
	outFileRef.write("</body>"+ "\n")
	outFileRef.write("</html>")
	outFileRef.close()
	# -------------------- end of function writeHTMLPage

def openHTMLPage():
	# code to open the html just created in the default Web browser.
	import urllib
	import webbrowser
	import os.path
	full_path = os.path.join( os.getcwd(), 'envoy-inventory.html' )
	fileURL = "file://" + urllib.request.pathname2url(full_path)
	webbrowser.open(fileURL)
	# -----------------------------------  end of function openHTMLPage()

def main():
	# main program function
	writeHTMLPage()
	openHTMLPage()
	# ----------------------   end of main program function
	
# run the program
main()
