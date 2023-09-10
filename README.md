# README #

## DehashedDomains ##

**Version 1.0.0**

### Purpose ###

This is a single Python script that interfaces with Dehashed's (https://dehashed.com/) API to quickly scour the dark web for breached company data given a user-supplied domain. 

### Setup ###

Prior to running the application, ensure that you have set your Dehashed login email and API key in your environment variables.

They need to be named "DEHASH_EMAIL" and "DEHASH_API" respectfully.

In Linux, add these environment variables by editing the following file as administrator:

```bash
If using 'vim' as an editor:

sudo vim /etc/environment

```

NOTE: After doing so, you will either need to logout/log back in or reboot your machine for the effects to take place. Simply running 'source /etc/environment' will not suffice as it is not a script.

ALSO: Please install 'name-that-hash' (more info found here: https://www.kali.org/tools/name-that-hash/) with apt to utilize the hash-identifier/organizer features like so : 

```bash
sudo apt install name-that-hash

```

After you do this, your script will be ready to run!

As stated before, you will need to provide a login email and API key both relevant to your *paid* Dehashed.com account as environment variables.

NOTE: If you or anyone else generates a new API key for any reason (which can easily be done with the push of a button in your Dehashed.com account settings), it will render all old API keys invalid.

### Usage ###

The script doesn't require any outside dependencies to run, just the newest version of Python. However, to have it automatically try to identify any returned hash types, install 'name-that-hash' as stated above. 

Upon running dehash.py, you must specify a single domain that you wish to gather information on with '--domain'

It will then attempt to:

Authenticate to your Dehashed.com account

Make a single API call to Dehashed that returns the first 10,000 results from Dehashed.com results on given domain

Create a new dynamically named folder in the current directory based on the provided domain that contains a:

* CSV file with ALL results

* Text file of usernames, one per line

* Text file of passwords, one per line

* Text file of credentials, (username:password) one per line (if this file is empty, there were no results that contained BOTH a username and a password)

* Text file of hashed passwords, one per line (alphabetically sorted)

* Text file of user emails, one per line (removes duplicates)

* Folder with files that are sorted by hash type (as accurate as the name-that-hash's Python module can be) and named according to Hashcat's mode number (specific to hash type).

NOTE: Each time the script is run, it *should* only consume 1 API token from Dehashed.com

### Cracking Results with Hashcat ###  

This script generates a folder named "hashcat-modes" that sorts all identified hashes by hash type. Once sorted by hash type, they are added to a text file named after the Hashcat mode associated with that hash type. 

This allows for easy cracking. For example, specify a text file named hashcat_mode_100 in the command like so (which correlates to the hash type SHA1 in hashcat): 

```bash
hashcat -a 0 -m 100 ./hashcat_mode_100 ~/Tools/rockyou.txt
```

### Example ###

```bash
python ./Documents/DehashedDomains/dehash.py --domain example.com

```

### Potential features to be added ###

Add redundant code to increase the 10,000 result limit to the API’s max of 30,000 (would increase the API token usage from 1 -> 3 per script run)

### Who do I talk to? ###

For any questions, comments, or other feedback please feel free to submit a pull request or ping me here on GitHub: https://github.com/jlanguell
