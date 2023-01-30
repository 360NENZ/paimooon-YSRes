import json
import os
from pathlib import Path
import re
import xlsxwriter

def weaponExtraction(textmap, weaponID, textMapLanguage):
    files = {"WeaponExcelConfigData": {},  # Main stats
            "WeaponCurveExcelConfigData": {},  # Stats curves
            "WeaponPromoteExcelConfigData": {}, # Weapon Ascension
            "WeaponLevelExcelConfigData": {},  # Level stats
            "MaterialExcelConfigData": {}, # Materials
            "EquipAffixExcelConfigData": {} # Refinement
            }

    for file in files:
        with open(os.path.join(os.path.dirname(__file__), f'./json/{file}.json'), encoding='utf-8') as json_file:
            files[file] = json.load(json_file)

    weapon(textmap, weaponID, files, textMapLanguage)

def weapon(textmap, weaponID, files, textMapLanguage):

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
    
    os.makedirs(os.path.join(os.path.dirname(__file__), f'res/{textMapLanguage}/'), exist_ok=True)
    with open(os.path.join(os.path.dirname(__file__), f'res/{textMapLanguage}/{weaponID}.json'), 'w', encoding='utf-8') as output_file:
        json.dump(json_dict, output_file, indent=4, ensure_ascii=False)

def ConvertText(desc):
    return "".join(re.split("<color.*?>(.+?)</color>", desc.replace("\\n", "\n")))

def GenerateRes(parseWeaponID, textMapLanguage):
    with open(os.path.join(os.path.dirname(__file__), f'json/TextMap_{textMapLanguage}.json'), encoding='utf-8') as textmap_json:
        textmap = json.load(textmap_json)

    weaponExtraction(textmap, parseWeaponID, textMapLanguage)

    with open(os.path.join(os.path.dirname(__file__), f'res/{textMapLanguage}/{parseWeaponID}.json'), encoding='utf-8') as dump:
        res = json.load(dump)
        
        wb = xlsxwriter.Workbook(f'./res/{parseWeaponID}.xlsx')
        ws = wb.add_worksheet()

        name_format = wb.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vjustify',
            'border': 1
        })

        desc_format = wb.add_format({
            'align': 'center',
            'valign': 'vjustify',
            'text_wrap': True,
            'border': 1
        })

        ws.merge_range('A1:H1', res["Name"], name_format)
        
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
        
        ws.merge_range('A2:B2', "Rarity", name_format)
        ws.merge_range('C2:D2', res["Rarity"], desc_format)

        ws.merge_range('A3:B3', "Weapon", name_format)
        ws.merge_range('C3:D3', weapon_dic[res["WeaponType"]], desc_format)

        for stat in res["StatsModifier"].keys():
            statCalc = res["StatsModifier"][stat]["Base"] * res["StatsModifier"][stat]["Levels"]["90"]
            
            if stat == "ATK":
                ws.merge_range('E2:F2', "Base ATK", name_format)
                ws.merge_range('G2:H2', int(statCalc + res["Ascension"]["6"]["FIGHT_PROP_BASE_ATTACK"]), desc_format)
            elif stat == "FIGHT_PROP_ELEMENT_MASTERY":
                ws.merge_range('E3:F3', asc_dic[stat], name_format)
                ws.merge_range('G3:H3', '{:0.0f}'.format(statCalc), desc_format )
            else:
                ws.merge_range('E3:F3', asc_dic[stat], name_format)
                ws.merge_range('G3:H3', '{:.1%}'.format(statCalc), desc_format )
        
        ws.merge_range('A6:J6', "Promote Costs", name_format)

        for i in range(6):
            items = []
            ws.write(i+6, 0, i+1, name_format)
            for j in res["Materials"][str(i+1)]["Mats"]:
                items.append(j["Name"] + " x" + str(j["Count"]))
            
            ws.merge_range(i+6, 1, i+6, 9, ", ".join(items), desc_format)

        ws.merge_range('A14:L14', res["Refinement"]["1"]["Name"], name_format)

        for i in range(5):
            items = []
            
            ws.merge_range(i+14, 0, i+14, 1, "Refinement Level " + str( i + 1), name_format)
            ws.merge_range(i+14, 2, i+14, 11, ConvertText(res["Refinement"][str(i+1)]["Desc"]), desc_format)
            ws.set_row(i+14, 100)

        wb.close()