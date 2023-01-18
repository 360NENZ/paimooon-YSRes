import json
import os
from pathlib import Path
import re

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

def ConvertText(desc):
    return "".join(re.split("<color.*?>(.+?)</color>", desc.replace("\\n", "\n")))

def GenerateRes(parseWeaponID, textMapLanguage):
    with open(os.path.join(os.path.dirname(__file__), f'json/TextMap_{textMapLanguage}.json')) as textmap_json:
        textmap = json.load(textmap_json)

    weaponExtraction(textmap, parseWeaponID)

    with open(os.path.join(os.path.dirname(__file__), f'res/{parseWeaponID}.json')) as dump:
        res = json.load(dump)
    
    weapon_dic = {
        "WEAPON_BOW": "Bow",
        "WEAPON_CATALYST": "Catalyst",
        "WEAPON_CLAYMORE": "Claymore",
        "WEAPON_POLE": "Polearm",
        "WEAPON_SWORD_ONE_HAND": "Sword"
    }

    asc_dic = {
        "FIGHT_PROP_HP_PERCENT": "HP%",
        "FIGHT_PROP_ATTACK_PERCENT": "ATK%",
        "FIGHT_PROP_DEFENSE_PERCENT": "DEF%",
        "FIGHT_PROP_ELEMENT_MASTERY": "Elemental Mastery",
        "FIGHT_PROP_CHARGE_EFFICIENCY": "Energy Recharge",
        "FIGHT_PROP_HEAL_ADD": "Heal Bonus",
        "FIGHT_PROP_CRITICAL_HURT": "Crit Damage",
        "FIGHT_PROP_CRITICAL": "Crit Rate",
        "FIGHT_PROP_PHYSICAL_ADD_HURT": "Phys Bonus",
        "FIGHT_PROP_GRASS_ADD_HURT": "Dendro Bonus",
        "FIGHT_PROP_ROCK_ADD_HURT": "Geo Bonus",
        "FIGHT_PROP_WIND_ADD_HURT": "Anemo Bonus",
        "FIGHT_PROP_WATER_ADD_HURT": "Hydro Bonus",
        "FIGHT_PROP_ICE_ADD_HURT": "Cryo Bonus",
        "FIGHT_PROP_ELEC_ADD_HURT": "Electro Bonus",
        "FIGHT_PROP_FIRE_ADD_HURT": "Pyro Bonus"
    }

    print("\n==========")
    print(res["Name"])
    print(res["Desc"])
    print(f'Rarity: {res["Rarity"]}')
    print(f'Type: {weapon_dic[res["WeaponType"]]}')

    for stat in res["StatsModifier"].keys():
        statCalc = res["StatsModifier"][stat]["Base"] * res["StatsModifier"][stat]["Levels"]["90"]
        
        if stat == "ATK":
            print(f'Base ATK: {int(statCalc + res["Ascension"]["6"]["FIGHT_PROP_BASE_ATTACK"])}')
        elif stat == "FIGHT_PROP_ELEMENT_MASTERY":
            print(f"{asc_dic[stat]}: {'{:0.0f}'.format(statCalc)}")
        else:
            print(f"{asc_dic[stat]}: {'{:.1%}'.format(statCalc)}")
    
    print()

    for i in "123456":
        items = []
        for j in res["Materials"][i]["Mats"]:
            items.append(j["Name"] + " x" + str(j["Count"]))

        print(", ".join(items))

    print()

    print(res["Refinement"]["1"]["Name"])
    for i in "12345":
        items = []
        print("\nRefinement Level", i)
        print(ConvertText(res["Refinement"][i]["Desc"]))

    print("==========")