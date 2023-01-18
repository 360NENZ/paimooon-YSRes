import json
import os
from pathlib import Path

def weaponExtraction(textmap, weaponID):
    files = {"WeaponExcelConfigData": {},  # Main stats
            "WeaponCurveExcelConfigData": {},  # Stats curves
            "WeaponPromoteExcelConfigData": {}, # Weapon Ascension
            "WeaponLevelExcelConfigData": {},  # Level stats
            "MaterialExcelConfigData": {}, # Materials
            "EquipAffixExcelConfigData": {} # Refinement
            }

    for file in files:
        with open(os.path.join(os.path.dirname(__file__), f'./json/{file}.json')) as json_file:
            files[file] = json.load(json_file)

    weapon(textmap, weaponID, files)

def weapon(textmap, weaponID, files):

    weaponData = list(filter(lambda x: x['id'] == weaponID, files["WeaponExcelConfigData"]))[0]

    # Stats
    weaponStats = {"ATK": {"Base": weaponData["weaponProp"][0]["initValue"],
                            "Levels": {}}}
    curves = [weaponData["weaponProp"][0]["type"]]

    # In case there is a substat (not the case for 1* and 2* weapons)
    if "propType" in weaponData["weaponProp"][1]:
        weaponStats[weaponData["weaponProp"][1]["propType"]] = {"Base": weaponData["weaponProp"][1]["initValue"], "Levels": {}}
        curves.append(weaponData["weaponProp"][1]["type"])

    for level in files["WeaponCurveExcelConfigData"]:
        for i, stat in enumerate(weaponStats):
            weaponStats[stat]["Levels"][level["level"]] = list(filter(lambda x: x["type"] == curves[i], level["curveInfos"]))[0]["value"]

    #XP requirements
    requiredXP = {}
    for level in files["WeaponLevelExcelConfigData"]:
        requiredXP[level["level"]] = level["requiredExps"][weaponData["rankLevel"] - 1]

    # Weapon Ascension
    ascensionData = list(filter(lambda x: x["weaponPromoteId"] == weaponData["weaponPromoteId"] if "promoteLevel" in x else None, files["WeaponPromoteExcelConfigData"]))
    ascensionData = sorted(ascensionData, key=lambda x: x["promoteLevel"])

    ascensionDict = {}
    ascMats = {}
    for asc in ascensionData:
        stat = list(filter(lambda x: "value" in x, asc["addProps"]))[0]
        ascensionDict[asc["promoteLevel"]] = {}
        ascensionDict[asc["promoteLevel"]][stat["propType"]] = stat["value"]
        ascMats[asc["promoteLevel"]] = { "Mats": [], "Cost": asc["coinCost"] if "coinCost" in asc else 0}

        for mat in list(filter(None, asc["costItems"])):
            # If mat dict isn't empty
            matData = list(filter(lambda x: x['id'] == mat["id"], files['MaterialExcelConfigData']))[0]
            dic = {"Name": textmap[str(matData["nameTextMapHash"])], "TextMapID": matData["nameTextMapHash"], "Count": mat["count"]}
            ascMats[asc["promoteLevel"]]["Mats"].append(dic)

    # Weapon Refinement
    refinementDict = {}
    refinementData = list(filter(lambda x: x["id"] == weaponData["skillAffix"][0], files["EquipAffixExcelConfigData"]))

    for ref in "12345":
        refinementDict[ref] = {}
        refinementDict[ref]["Name"] = textmap[str(refinementData[int(ref)-1]["nameTextMapHash"])]
        refinementDict[ref]["Desc"] = textmap[str(refinementData[int(ref)-1]["descTextMapHash"])]
        refinementDict[ref]["ParamList"] = refinementData[int(ref)-1]["paramList"]
    
    json_dict = {
        "Name": textmap[str(weaponData["nameTextMapHash"])],
        "Desc": textmap[str(weaponData["descTextMapHash"])],
        "WeaponType": weaponData["weaponType"],
        "Rarity": weaponData["rankLevel"],
        "StatsModifier": weaponStats,
        "XPRequirements": requiredXP,
        "Ascension": ascensionDict,
        "Refinement": refinementDict,
        "Materials": ascMats,
        "StoryFile": f"Weapon{weaponID}"
    }
    
    os.makedirs(os.path.join(os.path.dirname(__file__), f'res/'), exist_ok=True)
    with open(os.path.join(os.path.dirname(__file__), f'res/{weaponID}.json'), 'w') as output_file:
        json.dump(json_dict, output_file, indent=4, ensure_ascii=False)

def GenerateRes(parseWeaponID, textMapLanguage):
    with open(os.path.join(os.path.dirname(__file__), f'json/TextMap_{textMapLanguage}.json')) as textmap_json:
        textmap = json.load(textmap_json)

    weaponExtraction(textmap, parseWeaponID)
