import json

def remove_duplicates_from_dict_list(dict_list):
    seen = set()
    unique_dict_list = []
    for d in dict_list:
        # d['topics']=', '.join(d['topics'])
        d['lyrics'] = "."
        # 将字典转换为不可变的元组，以便可以放入集合中
        key_tuple = (d['name'], d['author'], d['album'], d['duration']) 
        # 如果元组不在集合中，则添加到集合和去重后的列表中 
        if key_tuple not in seen: 
            seen.add(key_tuple) 
            unique_dict_list.append(d)
        # dict_tuple = tuple(sorted(d.items()))
        # if dict_tuple not in seen:
        #     seen.add(dict_tuple)
        #     unique_dict_list.append(d)
    return unique_dict_list

def main():
    with open('./utils/songs.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    if isinstance(data, list) and all(isinstance(d, dict) for d in data):
        unique_data = remove_duplicates_from_dict_list(data)
        with open('./utils/songs2.json', 'w', encoding='utf-8') as file:
            json.dump(unique_data, file, ensure_ascii=False, indent=4)
    else:
        print("JSON 文件的格式不正确。")

if __name__ == "__main__":
    main()
