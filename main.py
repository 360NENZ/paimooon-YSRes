import character, weapon, parse, sys, argparse
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
    "MaterialExcelConfigData": Output.MaterialExcelConfig,
    "EquipAffixExcelConfigData": Output.EquipAffixExcelConfig,
    "WeaponExcelConfigData": Output.WeaponExcelConfig,
    "WeaponCurveExcelConfigData": Output.WeaponCurveExcelConfig,
    "WeaponPromoteExcelConfigData": Output.WeaponPromoteExcelConfig,
    "WeaponLevelExcelConfigData": Output.WeaponLevelExcelConfig,
}

def printUsage():
    print("""
usage: main.py [-t] [-e] [-o] [-l LANG] [-i ID] [-s] [-w]

Arguments:
    -t --textmap        # Dump TextMap (-l argument needed)
    -e --excel          # Dump ExcelBinOutput
    -o --output         # Generate character output (-l, -i argument needed)

    -l --lang [LANG]    # Set language (Example: KR)
    -i --id [ID]        # Set character id (Example: 10000078)

    -s                  # Xlsx skill short version

    -w --weapon         # Generate weapon output (-l, -i argument needed)
    """)
    sys.exit(1)

if __name__ == "__main__":
    print("YSRes BLK Parser Tool")
    print("Place .blk files in the YSRes/blk folder and run prepare.py first\n")

    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--textmap", dest="textmap", action="store_true")     # dump textmap
    parser.add_argument("-e", "--excel", dest="excel", action="store_true")         # dump excel
    parser.add_argument("-o", "--output", dest="output", action="store_true")       # generate output

    parser.add_argument("-l", "--lang", dest="lang", action="store")                # set language
    parser.add_argument("-i", "--id", type=int, dest="id", action="store")                    # set character id

    parser.add_argument("-s", "--short", dest="short", action="store_true")         # skill short

    parser.add_argument("-w", "--weapon", dest="weapon", action="store_true")
    
    args = parser.parse_args()

    if len(sys.argv) < 2:
        printUsage()

    if args.textmap:
        if args.lang is not None:
            parse.GetAllTextmaps(args.lang)
        else:
            printUsage()
    
    if args.excel:
        for i in parseList.keys():
            print("Parsing " + i)
            parse.UniversalParse(i, parseList[i])
    
    if args.output:
        if args.lang is not None and args.id is not None:
            print("Generating res...")
            character.GenerateRes(args.id, args.lang, args.short)
        else:
            printUsage()
    
    if args.weapon:
        if args.lang is not None and args.id is not None:
            print("Generating weapon res...")
            weapon.GenerateRes(args.id, args.lang)
        else:
            printUsage()
        
        