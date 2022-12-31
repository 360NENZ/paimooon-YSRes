import json
import os
import re
from pathlib import Path

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
        with open(os.path.join(os.path.dirname(__file__), f'./json/{file}.json')) as json_file:
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

    with open(os.path.join(os.path.dirname(__file__), f'./res/{charID}.json'), 'w') as output_file:
        json.dump(json_dict, output_file, indent=4, ensure_ascii=False)

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

    return paramList