from kaitaistruct import KaitaiStream
import xlsxwriter
from io import BytesIO
import glob, os, sys, json, re

import character

sys.path.append("./py")
from textmap import Textmap
from output import Output
from aux_types import AuxTypes

# add json if u want
parseList = {
    "AvatarExcelConfigData": Output.AvatarExcelConfig,
    "AvatarSkillDepotExcelConfigData": Output.AvatarSkillDepotExcelConfig,
    "AvatarSkillExcelConfigData": Output.AvatarSkillExcelConfig,
    "FetterInfoExcelConfigData": Output.FetterInfoExcelConfig,
    "AvatarTalentExcelConfigData": Output.AvatarTalentExcelConfig,
    "AvatarPromoteExcelConfigData": Output.AvatarPromoteExcelConfig,
    "ProudSkillExcelConfigData": Output.ProudSkillExcelConfig,
    "MaterialExcelConfigData": Output.MaterialExcelConfig
}

'''
    01/26692920 => CHS
    02/27251172 => 
    03/25181351 => 
    04/25776943 => EN
    05/20618174 => 
    06/25555476 => 
    07/30460104 => 
    08/32244380 => 
    09/22299426 => KR
    10/23331191 => 
    11/21030516 => 
    12/32056053 => 
    13/34382464 => 
'''

def GetAllTextmaps():
    global textMapLanguage
    output = dict()

    total = len(glob.glob('./bin/TextMap_' + textMapLanguage + '/*.bin'))
    cnt = 0

    for file in glob.glob('./bin/TextMap_' + textMapLanguage + '/*.bin'):

        cnt += 1
        print("Parsing textMap in progress [" + str(cnt) + "/" + str(total) + "]", end='\r')

        with open(file, 'rb') as f:
            stream = KaitaiStream(BytesIO(f.read()))
            obj = Textmap(stream)

            for block in obj.textmap:
                output[str(block.hash.value)] = block.string.data

    with open("./json/TextMap_" + textMapLanguage + ".json", "w", encoding='utf-8') as json_file:
        json.dump(output, json_file, indent=4, ensure_ascii=False)

# ExcelBinOutput Universal Parser
def UniversalParse(outputName, outputClass): 
    output_json = []
    with open(f"./bin/ExcelBinOutput/{outputName}.bin", "rb") as f:

        s = BytesIO(f.read())
        stream = KaitaiStream(s)

        obj = AuxTypes.VlqBase128LeS(stream)
        cnt = obj.value

        for i in range(cnt):
            # select parser class
            block = outputClass(stream)
            output_json.append(ParseProperties(block))

    with open(f'./json/{outputName}.json', 'w') as json_file:
        json.dump(output_json, json_file, indent=4)

def ParseProperties(block):

    # if u1 / s4 or sth
    if type(block) == float:
        return block

    if type(block) == int:
        if block == 1: # true value check
            return True
        return block

    # if string
    if type(block) == AuxTypes.String:
        return block.data

    # if leb128
    if type(block) == AuxTypes.VlqBase128LeU or type(block) == AuxTypes.VlqBase128LeS:
        return block.value

    # if EnumTalentFilterCond * hardcode
    if type(block) == Output.EnumTalentFilterCond:
        return ParseProperties(block.data)

    # else
    output_block = dict()

    # remove useless properties
    properties = [i for i in dir(block) if i[:1] != "_"]
    properties = [i for i in properties if i[:9] != "has_field"]
    if "bit_field" in properties: properties.remove("bit_field")
    if "from_bytes" in properties: properties.remove("from_bytes")
    if "from_file" in properties: properties.remove("from_file")
    if "from_io" in properties: properties.remove("from_io")
    if "close" in properties: properties.remove("close")

    for j in properties:

        # if array
        if "Array" in type(getattr(block, j)).__name__:
            output_block[lowCamelCase(j)] = [ParseProperties(i) for i in getattr(block, j).data]
        
        # if enum
        elif "Enum" in type(getattr(block, j)).__name__:
            
            if type(getattr(block, j).value) == int:
                output_block[lowCamelCase(j)] = getattr(block, j).value
            else:
                output_block[lowCamelCase(j)] = getattr(block, j).value.name.upper()

        # if dict (wip!)
        # return array as key - value
        else:
            # if name desc
            # return as nameTextMapHash descTextMapHash
            textmapHashes = [
                "name",
                "desc",
                "avatar_vision_befor",
                "avatar_vision_after",
                "avatar_constellation_befor",
                "avatar_constellation_after",
                "cv_chinese",
                "cv_japanese",
                "cv_english",
                "cv_korean",
            ]

            if j in textmapHashes :
                output_block[lowCamelCase(j + "_text_map_hash")] = ParseProperties(getattr(block, j))
            
            else:
                # return ?
                output_block[lowCamelCase(j)] = ParseProperties(getattr(block, j))

    return output_block

def lowCamelCase(snake_str):
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])

def GenerateRes(parseCharacterID, textMapLanguage):
    with open(os.path.join(os.path.dirname(__file__), f'json/TextMap_{textMapLanguage}.json')) as textmap_json:
        textmap = json.load(textmap_json)

    character.characterExtraction(textmap, parseCharacterID)

    with open(os.path.join(os.path.dirname(__file__), f'res/{parseCharacterID}.json')) as dump:
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

        print("Skill output selection")
        skillOutput = input("1~15 Full levels (f, default), 1 10 13 Short levels (s) : ")

        for i in range(len(res["Skills"])):
            ws.merge_range(current_row, 0, current_row, 15, res["Skills"][i]["Name"], name_format)
            current_row += 1
            ws.merge_range(current_row, 0, current_row, 15, ConvertText(res["Skills"][i]["Desc"]), desc_format)
            ws.set_row(current_row, 200) # Skill issue
            current_row += 1
            
            if skillOutput.lower() == "s" or skillOutput.lower() == "short":
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
    desc = desc.replace("\\n", "\n")

    pattern = "<color.*?>(.+?)</color>"
    desc_parsed = re.split(pattern, desc)
    
    return "".join(desc_parsed)

if __name__ == "__main__":
    print("YSRes blk parser tool")
    print("Place MiHoYoBinData .bin files in the ./bin folder")
    print("")

    dumpTextmap = input("Dump Textmap? (y/n, default=y) : ")

    if dumpTextmap == "" or dumpTextmap.lower() == "y" or dumpTextmap.lower() == "yes":
        textMapLanguage = input("Type the textMap Language (Example: KR) : ")
        print(f"Dumping TextMap_{textMapLanguage}...")
        GetAllTextmaps()

    dumpExcel = input("Dump ExcelBinOutput? (y/n, default=y) : ")
    if dumpExcel == "" or dumpExcel.lower() == "y" or dumpExcel.lower() == "yes":
        for i in parseList.keys():
            print("Parsing " + i)
            UniversalParse(i, parseList[i])
    
    parseExcel = input("Parse ExcelBinOutput? (y/n, default=y) : ")
    if parseExcel == "" or parseExcel.lower() == "y" or parseExcel.lower() == "yes":
        parseCharacterID = int(input("Type the character ID (Example: 10000078) : "))
        textMapLanguage = input("Type the textMap Language (Example: KR) : ")
        print("")
        print("Generating res via GenshinScripts...")
        GenerateRes(parseCharacterID, textMapLanguage)
