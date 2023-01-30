from kaitaistruct import KaitaiStream
import xlsxwriter
from io import BytesIO
import glob, os, sys, json, re
import subprocess
from multiprocessing import Process
from datetime import datetime

import character, parse

sys.path.append("./py")
from textmap import Textmap
from output import Output

# add json if u want
parseList = {
    "TowerScheduleExcelConfigData": Output.TowerScheduleExcelConfig,
    "TowerFloorExcelConfigData": Output.TowerFloorExcelConfig,
    "TowerLevelExcelConfigData": Output.TowerLevelExcelConfig,
    "DungeonLevelEntityConfigData": Output.DungeonLevelEntityConfig,
    "MonsterDescribeExcelConfigData": Output.MonsterDescribeExcelConfig,
}
    
def ConvertDescribeId(value, monsterDescribe):
    for i in monsterDescribe:
        if i["id"] == value:
            return i["nameTextMapHash"]

def ConvertText(desc):
    pattern = "<color.*?>(.+?)</color>"
    desc_parsed = re.split(pattern, desc)
    
    return "".join(desc_parsed)


if __name__ == '__main__':
    print("YSRes blk parser tool")
    print("Place MiHoYoBinData .bin files in the ./bin folder")
    print("")

    textMapLanguage = input("Type the textMap Language (Example: KR) : ")
    with open(f'./json/TextMap_{textMapLanguage}.json') as textmap_json:
        textmap = json.load(textmap_json)

    for i in parseList.keys():
        print("Parsing " + i)
        parse.UniversalParse(i, parseList[i])

    with open('./json/TowerScheduleExcelConfigData.json', 'r') as dump:
        towerSchedule = json.load(dump)
    with open('./json/TowerFloorExcelConfigData.json', 'r') as dump:
        towerFloor = json.load(dump)
    with open('./json/TowerLevelExcelConfigData.json', 'r') as dump:
        towerLevel = json.load(dump)
    with open('./json/DungeonLevelEntityConfigData.json', 'r') as dump:
        dungeonLevel = json.load(dump)
    with open('./json/MonsterDescribeExcelConfigData.json', 'r') as dump:
        monsterDescribe = json.load(dump)
    
    print("Last 5 abyss schedule_id:", ", ".join([str(i["scheduleId"]) for i in towerSchedule[-5:]]))

    scheduleIds = list(map(int, input("Type abyss schedule_ids (Example: 20036 20037 20038) : ").split()))
    scheduleId = scheduleIds[0] # hack

    ysVersion = input("Type anime game version : ")

    wb = xlsxwriter.Workbook(f'./res/{textMapLanguage}/{ysVersion}.xlsx')
    ws = wb.add_worksheet()

    name_format = wb.add_format({
        'bold': True,
        'align': 'center',
        'valign': 'vjustify',
        'border': 1
    })

    desc_format = wb.add_format({
        'align': 'left',
        'valign': 'vjustify',
        'text_wrap': True,
        'border': 1
    })

    current_row = 0
    ws.merge_range(current_row, 0, current_row, 9, ysVersion + " Abyss Info", name_format)
    current_row += 1
    ws.merge_range(current_row, 0, current_row, 9, datetime.now().strftime('%Y-%m-%d'), name_format)
    current_row += 1
    ws.merge_range(current_row, 0, current_row, 9, "Generated via YSRes", name_format)
    current_row += 1

    floorList = []
    openTime, closeTime = "", ""
    for i in towerSchedule:
        if i["scheduleId"] in scheduleIds:
            floorList = i["schedules"][0]["floorList"]
            
            if i["scheduleId"] == scheduleIds[0]: # useless anyway
                openTime = i["schedules"][0]["openTime"]
            if i["scheduleId"] == scheduleIds[-1]: # useless anyway
                closeTime = i["closeTime"] 

            ws.merge_range(current_row, 0, current_row, 9, textmap[str(i["buffname"])], desc_format)
            current_row += 1

            for j in dungeonLevel:
                if j["id"] == i["monthlyLevelConfigId"]:
                    ws.merge_range(current_row, 0, current_row, 9, ConvertText(textmap[str(j["descTextMapHash"])]), desc_format)
                    current_row += 1

            #print("icon: " + i["icon"]["data"])
    

    for i in towerFloor:
        if i["floorId"] in floorList:
            current_row += 1
            # print("===")
            # print("Floor id: " + str(i["floor_id"]["value"]))
            # print("Floor index: " + )
            # print("levelGroupId: " + str(i["level_group_id"]["value"]))
            
            ws.merge_range(current_row, 0, current_row, 9, str(i["floorIndex"]), name_format)
            current_row += 1
            ws.merge_range(current_row, 0, current_row, 9, "Version: " + ysVersion, desc_format)
            current_row += 1
            ws.merge_range(current_row, 0, current_row, 9, "Date: " + openTime + " ~ " + closeTime, desc_format)
            current_row += 1
            ws.merge_range(current_row, 0, current_row, 9, "Buff List:", desc_format)
            current_row += 1

            for j in dungeonLevel:
                if j["id"] == i["floorLevelConfigId"]:
                    if textmap[str(j["descTextMapHash"])] != "":
                        ws.merge_range(current_row, 0, current_row, 9, textmap[str(j["descTextMapHash"])], desc_format)
                        current_row += 1

            for j in towerLevel:
                if j["levelGroupId"] == i["levelGroupId"]:
                    floor = str(i["floorIndex"])
                    room = str(j["levelIndex"])
                    monsterLevel = str(j["monsterLevel"]+1)
                    # cond_upper = "/".join([str(conds["argument_list_upper"]["data"][1]["value"]) for conds in j["conds"]["data"]])
                    cond = "/".join([str(conds["argumentList"][1]) for conds in j["conds"]])
                    
                    ws.merge_range(current_row, 0, current_row, 9, floor + "-" + room + " " + cond + " Lv." + monsterLevel , name_format)
                    current_row += 1


                    monster1 = [textmap[str(ConvertDescribeId(monster, monsterDescribe))] for monster in j["firstMonsterList"]]
                    monster2 = [textmap[str(ConvertDescribeId(monster, monsterDescribe))] for monster in j["secondMonsterList"]]
                    
                    max_row = max(len(monster1), len(monster2))
                    
                    monster1 += [" " for _ in range(max_row)]
                    monster2 += [" " for _ in range(max_row)] # lazy hack

                    for idx in range(max_row):
                        ws.merge_range(current_row, 0, current_row, 4, monster1[idx], desc_format)
                        ws.merge_range(current_row, 5, current_row, 9, monster2[idx], desc_format)
                        current_row += 1
                    
            
    wb.close()
