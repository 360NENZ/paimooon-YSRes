import urllib.request, zipfile, subprocess, shutil, platform

# replace to the latest one
textMapLanguage = "KR"
xorKey = "0x94"

supportLanguage = {
    "CHS": "26692920",
    "EN": "25776943",
    "KR": "22299426"
}

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

# TextMap
subprocess.run(["./studio/AssetStudioCLI.exe", "./blk/" + supportLanguage[textMapLanguage] + ".blk", "./TextMap_" + textMapLanguage + "/", "--game", "GI", "--ai_file", "./ai.json", "--type", "MiHoYoBinData", "--xor_key", xorKey])

shutil.move("./ExcelBinOutput/MiHoYoBinData/", "./bin/ExcelBinOutput")
shutil.move("./TextMap_" + textMapLanguage + "/MiHoYoBinData/", "./bin/TextMap_" + textMapLanguage)

shutil.rmtree("./ExcelBinOutput")
shutil.rmtree("./TextMap_" + textMapLanguage)

print("Done")
