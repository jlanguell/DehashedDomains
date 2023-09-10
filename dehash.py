# 09-10-23
# https://github.com/jlanguell

# This Python script accepts a single domain in CLI args and environment variables to authenticate with Dehashed API, gather breached data on client, and write it all to the user's home directory.
# Additionally, any found hashes are checked with name-that-hash application (must be installed via Linux) for their hashcat *mode*, and saved accordingly to help speed up hash-cracking methods.

# NOTE: Script requires a domain as input with --domain or -d
# NOTE: Need to 'sudo apt install name-that-hash' to utilize automatic hash identifier function


# Imports

import sys
import os
import json
import csv
import argparse
import requests
import subprocess
from requests.auth import HTTPBasicAuth


def parse_args(): # Parse CLI args
	# CLI args
	parser = argparse.ArgumentParser(description = 'Dehashed Domain Scraper\nScript gathers the first 10,000 data entries, which is the max amount for Dehashed API queries.')
	parser.add_argument('-d', '--domain', help = 'Please specify a domain to scan such as "google.com"')
	args = parser.parse_args(sys.argv[1:])
	domain = args.domain
	if not domain:
		print("Please specify a domain with -d")
		sys.exit(0)
	return domain
	
	
def get_env(): # Authorize API connection via local environment variables (these need to be defined & stored in /etc/environment for linux)
	try:
		username = os.environ.get("DEHASH_EMAIL")
		key = os.environ.get("DEHASH_API")
		return username, key;
	except:
		print('Please ensure that you have login email and API key stored as environment variables named "DEHASH_EMAIL" & "DEHASH_API". For linux, you can create these by editing /etc/environment with sudo privileges.')
		sys.exit(0)


def http_request(url,username,key,headers_dict):
	request = requests.get(url, auth = HTTPBasicAuth(username,key),headers=headers_dict)
	json_data = json.loads(request.text)
	try:
		entries = json_data['entries']
	except:
		print('There was an error connecting to API, please ensure API email and key are set in your environment variables as "DEHASH_EMAIL" and "DEHASH_API" respectfully.')
		sys.exit(0)
	if not entries:
		print('No entries found for that domain.')
		sys.exit(0)
	return entries


def create_dir(domain):
	# Create Domain Folder in User Home Directory
	home_directory = os.path.expanduser('~')
	path = os.path.join(home_directory, "%s-dehashed" %domain)
	path_exist = os.path.exists(path)
	if not path_exist:
		os.makedirs(path)
		return path
	else:
		print('Scan results for this domain already exist at %s.\n\nPlease "rm -rf" existing Dehashed results folder for this domain or run script in a different directory.' %path)
		sys.exit(0)


def create_csv(path,entries):
	csv_file = open('%s/all-data.csv' %path, 'w')
	csv_writer = csv.writer(csv_file)
	count=0
	for entry in entries:
		if count == 0:
			header = entry.keys()
			csv_writer.writerow(header)
			count+=1	
		csv_writer.writerow(entry.values())   
	csv_file.close()


def write_file(path,entries,name):
	list=[]
	with open('%s/%s.txt' %(path,name), 'w') as write_file:
		
		if name=="creds": # Write username:password credentials to file whenever both are present in a single entry
			for entry in entries: 	 
					if entry['username'] != "" and entry['password'] != "":
						write_file.write(entry['username'] + ":" + entry['password'] + "\n")
			return
		
		if name=="hashes": # Write hashes to file (sorted alphabetically)
			for entry in entries:
				if entry['hashed_password'] != "":
					list.append(entry['hashed_password'] + "\n")
			list.sort()
			for item in list:
				write_file.write(item)
			return
		
		if name=="emails": # Write emails to file (sorted alphabetically)
			for entry in entries:
				if entry['email'] != "":
					list.append(entry['email'].lower() + "\n")  
			list.sort()
			list = set(list)
			for item in list:
				write_file.write(item)
			return

		for entry in entries: # Write username or password to respective file
			if entry['%s' %name] != "": 
				write_file.write(entry['%s' %name] + "\n")


def identify_hash(path,domain): # Must 'sudo apt install name-that-hash' prior to running this program
	path_exist = os.path.exists("%s/hashcat-modes/" %path)
	if not path_exist:
		os.makedirs("%s/hashcat-modes/" %path)
	else:
		print("An error occurred. Please make sure you delete or move any old file folders for %s in your home directory." %domain)
		sys.exit(0)
	result = subprocess.run('nth -f %s/hashes.txt -g' %(path), universal_newlines=True, capture_output=True, shell=True)
	with open('%s/hashcat-modes/name_that_hash.json' %path, "w") as f: # Creates a file containing all JSON from name-that-hash command
		f.write(result.stdout)
	with open('%s/hashcat-modes/name_that_hash.json' %path, "r") as f: # Tries to load JSON from nth, or catches "nth cmd not found" json null-loading error
		try:
			returned = json.load(f, strict=False)
		except json.decoder.JSONDecodeError as e:
			print("ERROR: HASH-IDENTIFIER DID NOT RUN \n\nPlease make sure you have already ran 'sudo apt install name-that-hash' prior!")
			sys.exit(0)
	    
	for key, value in returned.items(): # writes each hash & hashcat mode to respective file
		try:
			if value[0]["hashcat"] != "" or None:        
				mode = value[0]["hashcat"]	    
			elif value[1]["hashcat"] != "" or None:
				mode = value[1]["hashcat"]
			elif value[2]["hashcat"] != "" or None:
				mode = value[2]["hashcat"]
			else:
				print(key + "Not Identified")
			with open("%s/hashcat-modes/hashcat_mode_%s" %(path,mode), "a") as f:
				f.write(key + "\n")
	
		except: # writes hash to this file if not identified by nth
			with open("%s/hashcat-modes/hashcat_mode_NOTFOUND" %path, "a") as f: 
				f.write(key + "\n")
		

def main(): # Main function calls all other functions
	headers_dict = {'Accept':'application/json', # Prebuilt header variable
		'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.3538.77 Safari/537.36'} # Can't use python default User-Agent
	domain = parse_args() # Parse command line arguments to get domain
	url = 'https://api.dehashed.com/search?query=domain:"%s"&size=10000' % (domain) # API query address; can alter size within limits (see Dehashed documentation on their website)	
	username, key = get_env() # Get Dehashed username and key from ENV variables
	entries = http_request(url,username,key,headers_dict) # Authenticate and request data from Dehashed
	path = create_dir(domain) # Creates a folder in user's home directory to store all created data
	create_csv(path,entries) # Writes all Dehashed data to all-data.csv
	write_file(path,entries,name="username") # Writes data to username.txt
	write_file(path,entries,name="password") # Writes data to password.txt
	write_file(path,entries,name="creds") # Writes data to creds.txt
	write_file(path,entries,name="hashes") # Writes data to hashes.txt
	write_file(path,entries,name="emails") # Writes data to emails.txt
	identify_hash(path,domain) # Identifies hashes via name-that-hash subprocess and categorizes them all by file in /path/hashcat-modes/
	print("If the operation was successful, the data was saved to: %s" %path)	
	
	
if __name__ == "__main__": # Run application
	main()
	
	
