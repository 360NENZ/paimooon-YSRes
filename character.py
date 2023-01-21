import json
import os
import re
from pathlib import Path
import xlsxwriter

def characterExtraction(textmap, charID):
    files = {
        "AvatarExcelConfigData": {}, # Main character excel
        "AvatarPromoteExcelConfigData": {}, # Character ascension buff
        "AvatarSkillDepotExcelConfigData": {}, # Bindings between main excel and Talents/Skills/Constellations
        "AvatarSkillExcelConfigData": {},  # Main Skill Excel
        "AvatarTalentExcelConfigData": {}, # Character Talents
        "AvatarCurveExcelConfigData": {}, # HP/ATK/DEF calculations
        "AvatarPromoteExcelConfigData": {}, # Ascension const
        "MaterialExcelConfigData": {},   # Material Excel
        "ProudSkillExcelConfigData": {}, # Skills
        "FetterInfoExcelConfigData": {},  # Character info
    }

    for file in files:
        with open(os.path.join(os.path.dirname(__file__), f'./json/{file}.json'), encoding='utf-8') as json_file:
            files[file] = json.load(json_file)

    character(textmap, charID, files)

def character(textmap, charID, files):
    # Fix for Beidou, Keqing, Noelle
    correspondanceDict = {"charged attack cycling dmg": "charged attack spinning dmg",
                        "lightning stiletto dmg ": "lightning stiletto dmg",
                        "elemental burst dmg": "burst dmg"}

    avatarData = list(filter(lambda x: x['id'] == charID, files["AvatarExcelConfigData"]))[0]

    # Main stats curves
    HPcurve = list(filter(lambda x: x['type'] == "FIGHT_PROP_BASE_HP", avatarData["propGrowCurves"]))[0]["growCurve"]
    ATKcurve = list(filter(lambda x: x['type'] == "FIGHT_PROP_BASE_ATTACK", avatarData["propGrowCurves"]))[0]["growCurve"]
    DEFcurve = list(filter(lambda x: x['type'] == "FIGHT_PROP_BASE_DEFENSE", avatarData["propGrowCurves"]))[0]["growCurve"]

    statmodifier = {"HP":{},
                "ATK":{},
                "DEF":{},
                "Ascension": []}

    for level in files["AvatarCurveExcelConfigData"]:
        statmodifier["HP"][str(level["level"])] = list(filter(lambda x: x['type'] == HPcurve, level["curveInfos"]))[0]["value"]
        statmodifier["ATK"][str(level["level"])] = list(filter(lambda x: x['type'] == ATKcurve, level["curveInfos"]))[0]["value"]
        statmodifier["DEF"][str(level["level"])] = list(filter(lambda x: x['type'] == DEFcurve, level["curveInfos"]))[0]["value"]

    materialsDict = {"Ascensions": [],
                    "Talents": []}

    # Retrieving Ascension constants

    promoteConsts = list(filter(lambda x: x['avatarPromoteId'] == avatarData["avatarPromoteId"] if "promoteLevel" in x else None, files["AvatarPromoteExcelConfigData"]))
    promoteConsts = sorted(promoteConsts, key=lambda x: x['promoteLevel'])
    # 
    for i, prom in enumerate(promoteConsts):
        ascDict = {}
        for stat in prom['addProps']:
            ascDict[stat['propType']] = stat['value'] if 'value' in stat else 0.0
        statmodifier["Ascension"].append(ascDict)

        # Materials
        materialsDict["Ascensions"].append({"Mats": [], "Cost": prom["scoinCost"]})
        for mat in list(filter(None, prom["costItems"])):
            # If mat dict isn't empty
            matData = list(filter(lambda x: x['id'] == mat["id"], files['MaterialExcelConfigData']))[0]
            dic = {"Name": textmap[str(matData["nameTextMapHash"])], "Count": mat["count"]}
            materialsDict["Ascensions"][i]["Mats"].append(dic)

    # Corresponding character skill depot
    skillDepot = list(filter(lambda x: x['id'] == avatarData['skillDepotId'], files["AvatarSkillDepotExcelConfigData"]))[0]

    # Elemental burst skill ID -> skillDepot["EnergySkill"]
    # Other Skills
    skills = [i for i in skillDepot["skills"] if i != 0]
    skills.append(skillDepot["energySkill"])

    # Retreiving skills
    skillsList = []
    for skillNum, sk in enumerate(skills):
        main = list(filter(lambda x: x['id'] == sk, files["AvatarSkillExcelConfigData"]))[0]
        # Retrieving data for each skill level
        skillDetails = list(filter(lambda x: x['proudSkillGroupId'] == main["proudSkillGroupId"], files["ProudSkillExcelConfigData"]))
        skillDetails = sorted(skillDetails, key=lambda x:x['level'])
        
        skillDict = {"Name": textmap[str(main["nameTextMapHash"])],
                    "Desc": textmap[str(main["descTextMapHash"])],
                    "Param": {}}

        talentMatDict = []

        for count, skillLevel in enumerate(skillDetails):
            # Using a regex to filter the skill desc in the textmap to know how many parameters in ParamList correspond to the text.
            indexDesc, indexList = 0,0

            paramList = paramListCorrecter(skillLevel['paramList'], charID, skillNum)

            while textmap[str(skillLevel['paramDescList'][indexDesc])] != '':
                # Bugfix for normal attacks which use 5 hits instead of 6, the 6th would usually have a parameter of zero
                while paramList[indexList] == 0.0:
                    indexList += 1
                # Regex to find how many parameters correspond to the ParamDesc
                res = re.findall(r'(\{param.*?\})', textmap[str(skillLevel['paramDescList'][indexDesc])])
                if res != None:
                    # Text without parameters will be our key
                    key = textmap[str(skillLevel['paramDescList'][indexDesc])].split('|', 1)[0].lower()
                    # Correspondance bugfix
                    if key in correspondanceDict:
                        key = correspondanceDict[key]

                    if key not in skillDict["Param"]:
                        skillDict["Param"][key] = {"Name": textmap[str(skillLevel['paramDescList'][indexDesc])], "Levels": []}
                    # For parameters needed for a single description
                    paramlist = []
                    # If a param appears more than once (ex: Venti's normal attack)
                    oldparams = []
                    for i, par in enumerate(res):
                        # If we already used the said parameter, then we get its value from the list 
                        if par in oldparams:
                            ind = oldparams.index(par)
                            appParam = paramList[indexList-(i-ind)]
                        else:
                            appParam = paramList[indexList]
                            oldparams.append(par)
                            indexList += 1
                        paramlist.append(appParam)

                    skillDict["Param"][key]["Levels"].append(paramlist)
                indexDesc += 1
            matList = list(filter(None, skillLevel["costItems"]))

            if len(matList) > 0:
                talentMatDict.append({"Mats": [], "Cost": skillLevel["coinCost"]})
                for mat in matList:
                    matData = list(filter(lambda x: x['id'] == mat["id"], files['MaterialExcelConfigData']))[0]
                    dic = {"Name": textmap[str(matData["nameTextMapHash"])], "Count": mat["count"]}
                    talentMatDict[count-1]["Mats"].append(dic)

        materialsDict["Talents"].append(talentMatDict)
        skillsList.append(skillDict)

    # Passives Skills
    passiveskills = list(filter(None, skillDepot['inherentProudSkillOpens']))
    passList = []
    for pas in passiveskills:
        skill = list(filter(lambda x: x['proudSkillGroupId'] == pas['proudSkillGroupId'], files['ProudSkillExcelConfigData']))[0]
        dic = {"Name": textmap[str(skill["nameTextMapHash"])],
            "Desc": textmap[str(skill["descTextMapHash"])],
            "Unlock": pas['needAvatarPromoteLevel'] if 'needAvatarPromoteLevel' in pas else 0,
            "ParamList": skill["paramList"] # check the real value
        }
        passList.append(dic)

    # Constellations
    constellations = []
    for cons in sorted(skillDepot["talents"]):
        data = list(filter(lambda x: x['talentId'] == cons, files['AvatarTalentExcelConfigData']))[0]
        dic = {"Name": textmap[str(data["nameTextMapHash"])],
            "Desc": textmap[str(data["descTextMapHash"])],
            "ParamList": data["paramList"] # check the real value
        }
        constellations.append(dic)

    # Character info
    charaData = list(filter(lambda x: x['avatarId'] == avatarData['id'], files['FetterInfoExcelConfigData']))[0]

    charainfo = {
        "Birth": [charaData['infoBirthMonth'],charaData['infoBirthDay']],
        "Vision": textmap[str(charaData['avatarVisionBeforTextMapHash'])],
        "Constellation": textmap[str(charaData['avatarConstellationBeforTextMapHash'])],
        "Region": charaData['avatarAssocType'],
        "VA": {
            "Chinese": textmap[str(charaData['cvChineseTextMapHash'])],
            "Japanese": textmap[str(charaData['cvJapaneseTextMapHash'])],
            "English": textmap[str(charaData['cvEnglishTextMapHash'])],
            "Korean": textmap[str(charaData['cvKoreanTextMapHash'])]
        }
    }

    json_dict = {
        "Name": textmap[str(avatarData["nameTextMapHash"])],
        "Desc": textmap[str(avatarData["descTextMapHash"])],
        "CharaInfo": charainfo,
        "Weapon": avatarData["weaponType"],
        "Rarity": avatarData["qualityType"],
        "StaminaRecovery": avatarData["staminaRecoverSpeed"],
        "BaseHP": avatarData["hpBase"],
        "BaseATK": avatarData["attackBase"],
        "BaseDEF": avatarData["defenseBase"],
        "CritRate": avatarData["critical"],
        "CritDMG": avatarData["criticalHurt"],
        "StatsModifier": statmodifier,
        "Skills": skillsList,
        "Passives": passList,
        "Constellations": constellations,
        "Materials": materialsDict
    }

    os.makedirs(os.path.join(os.path.dirname(__file__), f'res/'), exist_ok=True)
    with open(os.path.join(os.path.dirname(__file__), f'res/{charID}.json'), 'w', encoding='utf-8') as output_file:
        json.dump(json_dict, output_file, indent=4, ensure_ascii=False)

# Excel Parser
def GenerateRes(parseCharacterID, textMapLanguage, skillOutput):
    with open(os.path.join(os.path.dirname(__file__), f'json/TextMap_{textMapLanguage}.json'), encoding='utf-8') as textmap_json:
        textmap = json.load(textmap_json)

    characterExtraction(textmap, parseCharacterID)

    with open(os.path.join(os.path.dirname(__file__), f'res/{parseCharacterID}.json'), encoding='utf-8') as dump:
        res = json.load(dump)
    
        wb = xlsxwriter.Workbook(f'./res/{parseCharacterID}.xlsx')
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

        rarity_dic = {
            "QUALITY_ORANGE": "5*",
            "QUALITY_PURPLE": "4*"
        }

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
        ws.merge_range('C2:D2', rarity_dic[res["Rarity"]], desc_format)

        ws.merge_range('A3:B3', "Weapon", name_format)
        ws.merge_range('C3:D3', weapon_dic[res["Weapon"]], desc_format)

        ws.merge_range('A4:B4', asc_dic[list(res["StatsModifier"]["Ascension"][5].keys())[3]], name_format)

        if list(res["StatsModifier"]["Ascension"][5].keys())[3] == "FIGHT_PROP_ELEMENT_MASTERY":
            ws.merge_range('C4:D4', "{0:.0f}".format(res["StatsModifier"]["Ascension"][5][list(res["StatsModifier"]["Ascension"][5].keys())[3]]), desc_format)
        else:
            ws.merge_range('C4:D4', "{0:.1%}".format(res["StatsModifier"]["Ascension"][5][list(res["StatsModifier"]["Ascension"][5].keys())[3]]), desc_format)

        ws.merge_range('E2:F2', "HP", name_format)
        ws.merge_range('G2:H2', int(res["BaseHP"] * res["StatsModifier"]["HP"]["90"] + res["StatsModifier"]["Ascension"][5]["FIGHT_PROP_BASE_HP"]) , desc_format)

        ws.merge_range('E3:F3', "ATK", name_format)
        ws.merge_range('G3:H3', int(res["BaseATK"] * res["StatsModifier"]["ATK"]["90"] + res["StatsModifier"]["Ascension"][5]["FIGHT_PROP_BASE_ATTACK"]) , desc_format)

        ws.merge_range('E4:F4', "DEF", name_format)
        ws.merge_range('G4:H4', int(res["BaseDEF"] * res["StatsModifier"]["DEF"]["90"] + res["StatsModifier"]["Ascension"][5]["FIGHT_PROP_BASE_DEFENSE"]) , desc_format)

        ws.merge_range('A6:J6', "Promote Costs", name_format)
        for i in range(6):
            ws.write(i+6, 0, i+1, name_format)

            items = []
            for j in res["Materials"]["Ascensions"][i]["Mats"]:
                items.append(j["Name"] + " x" + str(j["Count"]))

            ws.merge_range(i+6, 1, i+6, 9, ", ".join(items), desc_format)

        ws.merge_range('A14:J14', "Skill Upgrade Costs", name_format)
        for i in range(9):
            ws.write(i+14, 0, "Lv." + str(i+2), name_format)

            items = []
            for j in res["Materials"]["Talents"][0][i]["Mats"]:
                items.append(j["Name"] + " x" + str(j["Count"]))
            
            ws.merge_range(i+14, 1, i+14, 9, ", ".join(items), desc_format)

        ws.merge_range('A25:L25', "Constellations", name_format)
        ws.write('M25', "Real Value", desc_format) # via ParamList
        for i in range(6):
            ws.merge_range(i+25, 0, i+25, 1, res["Constellations"][i]["Name"], name_format)
            ws.merge_range(i+25, 2, i+25, 11, ConvertText(res["Constellations"][i]["Desc"]), desc_format)
            ws.write(i+25, 12, str([i for i in res["Constellations"][i]["ParamList"] if i != 0.0]), desc_format) 
            ws.set_row(i+25, 100)

        ws.merge_range('A33:L33', "Passives", name_format)
        ws.write('M33', "Real Value", desc_format) # via ParamList
        current_row = 33
        for i in range(len(res["Passives"])):
            ws.merge_range(i+33, 0, i+33, 1, res["Passives"][i]["Name"], name_format)
            ws.merge_range(i+33, 2, i+33, 11, ConvertText(res["Passives"][i]["Desc"]), desc_format)
            ws.write(i+33, 12, str([i for i in res["Passives"][i]["ParamList"] if i != 0.0]), desc_format)
            ws.set_row(i+33, 100) # Skill issue

        current_row = current_row + len(res["Passives"]) + 1

        for i in range(len(res["Skills"])):
            ws.merge_range(current_row, 0, current_row, 15, res["Skills"][i]["Name"], name_format)
            current_row += 1
            ws.merge_range(current_row, 0, current_row, 15, ConvertText(res["Skills"][i]["Desc"]), desc_format)
            ws.set_row(current_row, 200) # Skill issue
            current_row += 1
            
            if skillOutput:
                # start short version
                ws.merge_range(current_row, 0, current_row, 3, "Modifier", name_format)
                for j in [0, 9, 12]:
                    ws.merge_range(current_row, ([0, 9, 12].index(j) + 1) * 4, current_row, ([0, 9, 12].index(j) + 1) * 4 + 3, "Lv." + str(j+1), name_format)
                current_row += 1
                
                for j in list(res["Skills"][i]["Param"].keys()):
                    ws.merge_range(current_row, 0, current_row, 3, j.upper(), name_format)

                    param_form = res["Skills"][i]["Param"][j]["Name"].split("|")[1]

                    pattern = "\{param.*?:(.*?)\}"
                    param_parsed = re.split(pattern, param_form)
                    type_val = {
                        "P": "{0:.0%}",
                        "F1P": "{0:.1%}",
                        "F2P": "{0:.2%}",
                        "I": "{:0.0f}",
                        "F1": "{:0.1f}",
                        "F2": "{:0.2f}",
                    }
                    
                    for k in [0, 9, 12]:
                        values = list(res["Skills"][i]["Param"][j]["Levels"][k])
                        out_val = ""
                        for val in param_parsed:
                            if val in list(type_val.keys()):
                                out_val += type_val[val].format(values.pop(0))
                            else:
                                out_val += val

                        ws.merge_range(current_row, ([0, 9, 12].index(k) + 1) * 4, current_row, ([0, 9, 12].index(k) + 1) * 4 + 3, out_val, desc_format)
                    current_row += 1
                # end

            else:
                # start full version
                ws.write(current_row, 0, "Modifier", name_format)
                for j in range(15):
                    ws.write(current_row, j+1, "Lv." + str(j+1), name_format)
                current_row += 1

                for j in list(res["Skills"][i]["Param"].keys()):
                    ws.write(current_row, 0, j.upper(), name_format)

                    param_form = res["Skills"][i]["Param"][j]["Name"].split("|")[1]

                    pattern = "\{param.*?:(.*?)\}"
                    param_parsed = re.split(pattern, param_form)
                    type_val = {
                        "P": "{0:.0%}",
                        "F1P": "{0:.1%}",
                        "F2P": "{0:.2%}",
                        "I": "{:0.0f}",
                        "F1": "{:0.1f}",
                        "F2": "{:0.2f}",
                    }
                    
                    for k in range(15):
                        values = list(res["Skills"][i]["Param"][j]["Levels"][k])
                        out_val = ""
                        for val in param_parsed:
                            if val in list(type_val.keys()):
                                out_val += type_val[val].format(values.pop(0))
                            else:
                                out_val += val

                        ws.write(current_row, k+1, out_val, desc_format)
                    current_row += 1
                # end
            current_row += 1
        wb.close()

def ConvertText(desc):
    return "".join(re.split("<color.*?>(.+?)</color>", desc.replace("\\n", "\n")))

# A hardcoded function which corrects the paramList of some skills
def paramListCorrecter(paramList, charaID, skillNum):
    # Amber
    if charaID == 10000021:
        # Elemental Skill
        if skillNum == 1:
            paramList.pop(2)
        # Elemental Burst
        elif skillNum == 2:
            paramList.insert(1, paramList.pop(3))
            paramList.insert(2, paramList.pop(4))
    # Barbara's Elemental Skill
    elif charaID == 10000014 and skillNum == 1:
        paramList.insert(0, paramList.pop(2))
        paramList.insert(1, paramList.pop(3))
    # Chongyun's Elemental Skill
    elif charaID == 10000036 and skillNum == 1:
        paramList.insert(2, paramList.pop(3))
    # Diona
    elif charaID == 10000039:
        # Elemental Skill
        if skillNum == 1:
            paramList.insert(3, paramList.pop(5))
        # Elemental Burst
        elif skillNum == 2:
            paramList.insert(4, paramList.pop(6))
    # Klee
    elif charaID == 10000029:
        # Elemental Skill
        if skillNum == 1:
            paramList.pop(1)
            paramList.pop(1)
        # Elemental Burst
        elif skillNum == 2:
            paramList.insert(1, paramList.pop(4))
            paramList.pop(4)
    # Lisa's Elemental Skill
    elif charaID == 10000006 and skillNum == 1:
        paramList.insert(0, paramList.pop(5))
        paramList.insert(1, paramList.pop(6))
    # Mona's Elemental Burst
    elif charaID == 10000041 and skillNum == 2:
        paramList.insert(2, paramList.pop(9))
        paramList.pop(3)
    # Ningguang's Elemental Skill
    elif charaID == 10000027 and skillNum == 1:
        paramList.pop(0)
        paramList.insert(0, paramList.pop(1))
    # Noelle's Elemental Skill
    elif charaID == 10000034 and skillNum == 1:
        paramList.insert(0, paramList.pop(5))
        paramList.insert(2, paramList.pop(6))
        paramList.insert(4, paramList.pop(7))
    # Qiqi
    elif charaID == 10000035:
        if skillNum == 1:
            paramList.insert(0, paramList.pop(7))
        elif skillNum == 2:
            paramList.insert(0, paramList.pop(2))
    # Tartaglia
    elif charaID == 10000033:
        # Normal Attack
        if skillNum == 0:
            paramList.insert(10, paramList.pop(13))
        # Elemental Skill
        elif skillNum == 1:
            paramList.insert(10, paramList.pop(11))
    # Xinyan's Elemental Burst
    elif charaID == 10000044 and skillNum == 2:
        paramList.insert(2, paramList.pop(4))

    # Yaoyao's Elemental Burst
    if charaID == 10000077 and skillNum == 2:
        paramList.insert(0, paramList.pop(3))

    if charaID == 10000080 and skillNum == 2:
        paramList.insert(0, paramList.pop(1))
        paramList.insert(2, paramList.pop(3))

    return paramList