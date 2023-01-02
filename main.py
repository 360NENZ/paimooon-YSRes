import character, parse, sys
sys.path.append("./py")

from output import Output

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

if __name__ == "__main__":
    print("YSRes blk parser tool")
    print("Place MiHoYoBinData .bin files in the ./bin folder")
    print("")

    dumpTextmap = input("Dump Textmap? (y/n, default=y) : ")

    if dumpTextmap == "" or dumpTextmap.lower() == "y" or dumpTextmap.lower() == "yes":
        textMapLanguage = input("Type the textMap Language (Example: KR) : ")
        print(f"Dumping TextMap_{textMapLanguage}...")
        parse.GetAllTextmaps(textMapLanguage)

    dumpExcel = input("Dump ExcelBinOutput? (y/n, default=y) : ")
    if dumpExcel == "" or dumpExcel.lower() == "y" or dumpExcel.lower() == "yes":
        for i in parseList.keys():
            print("Parsing " + i)
            parse.UniversalParse(i, parseList[i])
    
    parseExcel = input("Parse ExcelBinOutput? (y/n, default=y) : ")
    if parseExcel == "" or parseExcel.lower() == "y" or parseExcel.lower() == "yes":
        parseCharacterID = int(input("Type the character ID (Example: 10000078) : "))
        textMapLanguage = input("Type the textMap Language (Example: KR) : ")
        skillOutput = input("\nType the skill output type\n1~15 Full levels (f, default), 1 10 13 Short levels (s) : ")
        print("")
        print("Generating res...")
        character.GenerateRes(parseCharacterID, textMapLanguage, skillOutput)
        print("Done")
