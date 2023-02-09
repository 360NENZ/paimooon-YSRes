import urllib.request, zipfile, subprocess, shutil, platform

# replace to the latest one
# textMapLanguageList = ["KR", "CHS"]
xorKey = "0x95"

supportLanguage = {
    "CHS": "26692920",
    "CHT": "27251172",
    "DE": "25181351",
    "EN": "25776943",
    "ES": "20618174",
    "FR": "25555476",
    "ID": "30460104",
    "JP": "32244380",
    "KR": "22299426",
    "PT": "23331191",
    "RU": "21030516",
    "TH": "32056053",
    "VI": "34382464"
}

# exclude this if not needed
textMapLanguageList = supportLanguage.keys()


asset_studio = "https://github.com/paimooon/YSRes/files/10318744/net472.zip"
mapped_ai_json = "https://github.com/14eyes/gi-asset-indexes/blob/master/mapped/GenshinImpact_3.3.50_beta.zip_31049740.blk.asset_index.json?raw=true"


print("YSRes one-click script")
print("Remember to put blks in YSRes/blk folder")
print("")
print("Downloading studio...")
urllib.request.urlretrieve(asset_studio, "studio.zip")

print("Downloading AI json...")
urllib.request.urlretrieve(mapped_ai_json, "ai.json")

print("Unzipping studio...")
zipfile.ZipFile("studio.zip", 'r').extractall("./studio/")

# ExcelBinOutput
subprocess.run(["./studio/AssetStudioCLI.exe", "./blk/25539185.blk", "./ExcelBinOutput/", "--game", "GI", "--ai_file", "./ai.json", "--type", "MiHoYoBinData", "--xor_key", xorKey])
shutil.move("./ExcelBinOutput/MiHoYoBinData/", "./bin/ExcelBinOutput")
shutil.rmtree("./ExcelBinOutput")

# TextMap
for textMapLanguage in textMapLanguageList:
    try:
        subprocess.run(["./studio/AssetStudioCLI.exe", "./blk/" + supportLanguage[textMapLanguage] + ".blk", "./TextMap_" + textMapLanguage + "/", "--game", "GI", "--ai_file", "./ai.json", "--type", "MiHoYoBinData", "--xor_key", xorKey])
        shutil.move("./TextMap_" + textMapLanguage + "/MiHoYoBinData/", "./bin/TextMap_" + textMapLanguage)
        shutil.rmtree("./TextMap_" + textMapLanguage)
    except:
        pass

print("Done")
