from kaitaistruct import KaitaiStream
from io import BytesIO
import os, sys, json, re
import subprocess

# Put configavatar_bin name at the below
chars_to_be_parsed = ["ConfigAvatar_Alhatham", "ConfigAvatar_Yaoyao"]

def MakeJson(avatar):
    cmd = ['ksdump', '-f', 'json', './bin/BinOutput' + avatar + '.bin', './ksy/BinOut/Avatar/config_avatar.ksy']
    output = json.loads('{"abilities": []}')
    ksy = {}

    with open('./json/Dump_' + avatar + '.json', 'w') as out:
        return_code = subprocess.call(cmd, stdout=out)

    with open('./json/Dump_' + avatar + '.json', 'r') as dump:
        ksy = json.load(dump)
        abilities = []

        # we will only parse abilities cz grasscutter only require this
        for i in ksy["abilities"]["data"]:
            ability = dict()
            ability["abilityID"] = i["ability_id"]["data"]
            ability["abilityName"] = i["ability_name"]["data"]
            output["abilities"].append(ability)

    with open("./json/" + avatar + ".json", "w") as json_file:
        json.dump(output, json_file, indent=4)

for avatar in chars_to_be_parsed:
    MakeJson(avatar)