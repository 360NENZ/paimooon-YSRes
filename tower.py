from kaitaistruct import KaitaiStream
import xlsxwriter
from io import BytesIO
import glob, os, sys, json, re
import subprocess
from multiprocessing import Process
from datetime import datetime

sys.path.append("./py")
from textmap import Textmap

def DumpTowerSchedule():
    cmd = ['ksdump', '-f', 'json', './bin/ExcelBinOutput/TowerScheduleExcelConfigData.bin', './ksy/tower_schedule.ksy']

    with open('./json/Dump_TowerScheduleExcelConfigData.json', 'w') as out:
        return_code = subprocess.call(cmd, stdout=out)

def DumpTowerFloor():
    cmd = ['ksdump', '-f', 'json', './bin/ExcelBinOutput/TowerFloorExcelConfigData.bin', './ksy/tower_floor.ksy']

    with open('./json/Dump_TowerFloorExcelConfigData.json', 'w') as out:
        return_code = subprocess.call(cmd, stdout=out)

def DumpTowerLevel():
    cmd = ['ksdump', '-f', 'json', './bin/ExcelBinOutput/TowerLevelExcelConfigData.bin', './ksy/tower_level.ksy']

    with open('./json/Dump_TowerLevelExcelConfigData.json', 'w') as out:
        return_code = subprocess.call(cmd, stdout=out)

def DumpDungeonLevel():
    cmd = ['ksdump', '-f', 'json', './bin/ExcelBinOutput/DungeonLevelEntityConfigData.bin', './ksy/dungeon_level.ksy']

    with open('./json/Dump_DungeonLevelEntityConfigData.json', 'w') as out:
        return_code = subprocess.call(cmd, stdout=out)

def DumpMonsterDescribe():
    cmd = ['ksdump', '-f', 'json', './bin/ExcelBinOutput/MonsterDescribeExcelConfigData.bin', './ksy/monster_describe.ksy']

    with open('./json/Dump_MonsterDescribeExcelConfigData.json', 'w') as out:
        return_code = subprocess.call(cmd, stdout=out)


def GenerateTower():
    textMapLanguage = input("Type the textMap Language (Example: KR) : ")
    with open(f'./json/TextMap_{textMapLanguage}.json') as textmap_json:
        textmap = json.load(textmap_json)

    with open('./json/Dump_TowerScheduleExcelConfigData.json', 'r') as dump:
        towerSchedule = json.load(dump)
    with open('./json/Dump_TowerFloorExcelConfigData.json', 'r') as dump:
        towerFloor = json.load(dump)
    with open('./json/Dump_TowerLevelExcelConfigData.json', 'r') as dump:
        towerLevel = json.load(dump)
    with open('./json/Dump_DungeonLevelEntityConfigData.json', 'r') as dump:
        dungeonLevel = json.load(dump)
    with open('./json/Dump_MonsterDescribeExcelConfigData.json', 'r') as dump:
        monsterDescribe = json.load(dump)
    
    print("Last 5 abyss schedule_id:", ", ".join([str(i["schedule_id"]["value"]) for i in towerSchedule["block"][-5:]]))

    scheduleIds = list(map(int, input("Type abyss schedule_ids (Example: 20036 20037 20038) : ").split()))
    scheduleId = scheduleIds[0] # hack

    ysVersion = input("Type genshin version : ")

    wb = xlsxwriter.Workbook(f'./res/{ysVersion}.xlsx')
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
    for i in towerSchedule["block"]:
        if i["schedule_id"]["value"] in scheduleIds:
            floorList = [i["value"] for i in i["schedules"]["data"][0]["floor_list"]["data"]]
            
            if i["schedule_id"]["value"] == scheduleIds[0]: # useless anyway
                openTime = i["schedules"]["data"][0]["open_time"]["data"]
            if i["schedule_id"]["value"] == scheduleIds[-1]: # useless anyway
                closeTime = i["close_time"]["data"] 

            ws.merge_range(current_row, 0, current_row, 9, textmap[str(i["buffname"]["value"])], desc_format)
            current_row += 1

            for j in dungeonLevel["block"]:
                if j["id"]["value"] == i["monthly_level_config_id"]["value"]:
                    ws.merge_range(current_row, 0, current_row, 9, ConvertText(textmap[str(j["desc"]["value"])]), desc_format)
                    current_row += 1

            #print("icon: " + i["icon"]["data"])
    

    for i in towerFloor["block"]:
        if i["floor_id"]["value"] in floorList:
            current_row += 1
            # print("===")
            # print("Floor id: " + str(i["floor_id"]["value"]))
            # print("Floor index: " + )
            # print("levelGroupId: " + str(i["level_group_id"]["value"]))
            
            ws.merge_range(current_row, 0, current_row, 9, str(i["floor_index"]["value"]), name_format)
            current_row += 1
            ws.merge_range(current_row, 0, current_row, 9, "Version: " + ysVersion, desc_format)
            current_row += 1
            ws.merge_range(current_row, 0, current_row, 9, "Date: " + openTime + " ~ " + closeTime, desc_format)
            current_row += 1
            ws.merge_range(current_row, 0, current_row, 9, "Buff List:", desc_format)
            current_row += 1

            for j in dungeonLevel["block"]:
                if j["id"]["value"] == i["floor_level_config_id"]["value"]:
                    if textmap[str(j["desc"]["value"])] != "":
                        ws.merge_range(current_row, 0, current_row, 9, textmap[str(j["desc"]["value"])], desc_format)
                        current_row += 1

            for j in towerLevel["block"]:
                if j["level_group_id"]["value"] == i["level_group_id"]["value"]:
                    floor = str(i["floor_index"]["value"])
                    room = str(j["level_index"]["value"])
                    monsterLevel = str(j["monster_level"]["value"]+1)
                    # cond_upper = "/".join([str(conds["argument_list_upper"]["data"][1]["value"]) for conds in j["conds"]["data"]])
                    cond = "/".join([str(conds["argument_list"]["data"][1]["value"]) for conds in j["conds"]["data"]])
                    
                    ws.merge_range(current_row, 0, current_row, 9, floor + "-" + room + " " + cond + " Lv." + monsterLevel , name_format)
                    current_row += 1


                    monster1 = [textmap[str(ConvertDescribeId(monster["value"], monsterDescribe))] for monster in j["first_monster_list"]["data"]]
                    monster2 = [textmap[str(ConvertDescribeId(monster["value"], monsterDescribe))] for monster in j["second_monster_list"]["data"]]
                    
                    max_row = max(len(monster1), len(monster2))
                    
                    monster1 += [" " for _ in range(max_row)]
                    monster2 += [" " for _ in range(max_row)] # lazy hack

                    for idx in range(max_row):
                        ws.merge_range(current_row, 0, current_row, 4, monster1[idx], desc_format)
                        ws.merge_range(current_row, 5, current_row, 9, monster2[idx], desc_format)
                        current_row += 1
                    
            
    wb.close()
    
def ConvertDescribeId(value, monsterDescribe):
    for i in monsterDescribe["block"]:
        if i["id"]["value"] == value:
            return i["name"]["value"]

def ConvertText(desc):
    pattern = "<color.*?>(.+?)</color>"
    desc_parsed = re.split(pattern, desc)
    
    return "".join(desc_parsed)


if __name__ == '__main__':
    print("YSRes blk parser tool")
    print("Place MiHoYoBinData .bin files in the ./bin folder")
    print("")
    
    # Arg would support later

    dumpTower = input("Dump tower? : ")

    if dumpTower == "y": # I'm lazy
        DumpTowerFloor()
        DumpTowerLevel()
        DumpTowerSchedule()
        DumpMonsterDescribe()
        DumpDungeonLevel()
    
    parseTower = input("Parse tower? : ")

    if parseTower == "y":
        GenerateTower()
