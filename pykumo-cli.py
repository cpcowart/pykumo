#!/usr/bin/env python3
""" Module to interact with Mitsubishi KumoCloud devices via their local API.
"""

import json
import hashlib
import base64
import requests
from pykumo import pykumo
from cmd import Cmd
from getpass import getpass
from pprint import pprint

class pyKumoCLI(Cmd):
    def __init__(self):
        super().__init__()
        self.prompt = 'kumo> '

    def preloop(self):
        print('Welcome to pyKumoCLI!')

        username = input('Kumo Cloud username: ')
        password = getpass(prompt='Kumo Cloud Password: ', stream=None)

        url = "https://geo-c.kumocloud.com/login"                                     
        headers = {'Accept': 'application/json, text/plain, */*',                     
                   'Accept-Encoding': 'gzip, deflate, br',                            
                   'Accept-Language': 'en-US,en',                                     
                   'Content-Type': 'application/json'}                                
        body = '{"username":"%s","password":"%s","appVersion":"2.2.0"}' % (username, password)                                                                           
        response = requests.post(url, headers=headers, data=body)                     
    
        self.cloud_dict = response.json()          
        self.zones = []

        for child in self.cloud_dict[2]['children']:
            for zone in child['zoneTable'].values():
                name = zone['label']
                address = zone['address']
                config = {'password': zone['password'],
                          'crypto_serial': zone['cryptoSerial']}
                pk = pykumo.PyKumo(name, address, config)
                self.zones.append({'name': name, 'pykumo': pk})

    def do_exit(self, inp):
        '''Exit the cli.'''
        return True

    do_EOF = do_exit

    def emptyline(self):
        pass

    def do_zones(self, inp):
        '''Lists zones found in your Kumo Cloud account'''
        for zone in self.zones:
            print(zone['name'])

    def do_update(self, inp):
        for zone in self.zones:
            zone['pykumo'].poll_status()

    def do_get(self, inp):
        '''get zone_name attribute1 [ attribute2 ... ]'''
        cmd = inp.split()
        zone = cmd.pop(0)
        try:
            pk = next(z for z in self.zones if z['name'] == zone)['pykumo']
        except StopIteration:
            print("No such zone %s" % zone)

        for attr in cmd:
            try:
                get = getattr(pk, "get_%s" % attr)
            except AttributeError:
                print("No such attribute: %s" % attr)
                continue
            print("%s - %s: %s" % (zone, attr, get()))

def main():
    """ Entry point
    """
    cli = pyKumoCLI()
    cli.cmdloop()

if __name__ == '__main__':
    main()
