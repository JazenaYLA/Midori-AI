import os
import json
import hashlib
import platform
import argparse
import requests

from cryptography.fernet import Fernet

parser = argparse.ArgumentParser(description="N/A")
parser.add_argument("-u", "--username", required=True, type=str, help="Username to use for the server...")
parser.add_argument("-byp", "--bypassplatform", required=False, type=str, help="Bypass platform check")
parser.add_argument("-byos", "--bypassoscheck", required=False, type=str, help="Bypass OS check")
parser.add_argument("-unsafe", "--unsafe", required=False, action='store_true', help="Enable unsafe mode")
parser.add_argument("-mkuser", "--makeuser", required=False, action='store_true', help="Enable makeuser mode")
args = parser.parse_args()

pre_unsafe = str(args.unsafe).lower()
pre_makeuser = str(args.makeuser).lower()

if len(str(args.username)) < 6:
    print("Please make your username 6 or more letters...")
    exit()

if pre_makeuser == "true":
    makeuser = True
else: 
    makeuser = False

if pre_unsafe == "true":
    print("UNSAFE MODE: True")
    print("UNSAFE MODE: Please note this is really unsafe and you could be banned from logging in")
    print("UNSAFE MODE: Only use this if you are a cluster member or if Midori AI asked you to...")
    unsafe = True
else: 
    unsafe = False

key_one = Fernet.generate_key()

fernet_one = Fernet(key_one)

if not unsafe:
    stats = {
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
        },
    }

    stats_json = json.dumps(stats)
    os_version = os.uname().release

    hash_object = hashlib.sha512(stats_json.encode())
    os_hash_object = hashlib.sha512(os_version.encode())

    hash_hex = hash_object.hexdigest()
    os_hash_hex = os_hash_object.hexdigest()

else:
    hash_hex = str(args.bypassplatform).lower()
    os_hash_hex = str(args.bypassoscheck).lower()

encrypted_platform_one = fernet_one.encrypt(str(hash_hex).encode())
encrypted_os_version_one = fernet_one.encrypt(str(os_hash_hex).encode())

if makeuser:
    invite_key = input("Please enter the invite key from Midori AI")
    try:
        response = requests.post("https://tea-pot.midori-ai.xyz/make_user_user", 
            headers=
            {
                "username": f"{str(args.username)}", 
                "invite_key": f"{str(invite_key)}", 
                "platform" : f"{encrypted_platform_one.decode()}", 
                "os_version" : f"{encrypted_os_version_one.decode()}", 
                "api_verison" : f"{key_one.decode()}"
            }
            )
        
        if response.status_code == 200:
            print("User Made Logging in!")
        else:
            error_message = response.text
            raise Exception(f"Server returned status code {response.status_code}: {error_message}")

    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)

try:
    response = requests.post("https://tea-pot.midori-ai.xyz/get_api_key_user", 
        headers=
        {
            "username": f"{str(args.username)}", 
            "platform" : f"{encrypted_platform_one.decode()}", 
            "os_version" : f"{encrypted_os_version_one.decode()}", 
            "api_verison" : f"{key_one.decode()}"
        }
        )
    
    if response.status_code == 200:
        api_key = response.text
        os.environ["MIDORI_AI_API_KEY_TEMP"] = api_key
    else:
        error_message = response.text
        raise Exception(f"Server returned status code {response.status_code}: {error_message}")

except Exception as e:
    print(f"Error: {str(e)}")
    exit(1)