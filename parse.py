from kaitaistruct import KaitaiStream
from io import BytesIO
import glob, sys, json, os

sys.path.append("./py")
from textmap import Textmap
from output import Output
from aux_types import AuxTypes

# TextMap Parser
def GetAllTextmaps(textMapLanguage):
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

    os.makedirs("./json", exist_ok=True)
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

    os.makedirs("./json", exist_ok=True)
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
    