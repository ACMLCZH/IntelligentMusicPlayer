import json


def remove_duplicates_from_dict_list(dict_list):
    seen = set()
    unique_dict_list = []
    for d in dict_list:
        d["lyrics"] = "."
        key_tuple = (d["name"], d["author"], d["album"], d["duration"])
        if key_tuple not in seen:
            seen.add(key_tuple)
            unique_dict_list.append(d)
    return unique_dict_list


def main():
    with open("./utils/songs.json", "r", encoding="utf-8") as file:
        data = json.load(file)

    if isinstance(data, list) and all(isinstance(d, dict) for d in data):
        unique_data = remove_duplicates_from_dict_list(data)
        with open("./utils/songs2.json", "w", encoding="utf-8") as file:
            json.dump(unique_data, file, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
