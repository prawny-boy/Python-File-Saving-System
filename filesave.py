"""Manipulate text in files for saving, loading and reading.

Hierarchy system to store data in a text file.
Group -> Subgroup -> Item -> Data

Made by Sean Chan, 2025. All rights reserved.

This module uses terms to refer to different parts of file saving and data.
- Group: A group is a collection of subgroups. It is represented by a line starting and ending with an asterisk (*).
- Subgroup: A subgroup is a collection of items. It is represented by a line ending with a colon (:).
- Item: An item is a single piece of data. It is represented by a line with a name and _data_ separated by a pipe (|).
- Data: Data is the value associated with an item. Types include str, int, float, list, dict, tuple, bool, and None.
- Settings: Settings are special lines that start and end with parentheses (()). They are not part of the data structure but can be used for configuration.
- File: A file is a text file that contains the groups, subgroups, items, and data. It is represented by a .txt file.
- File System: The file system is the overall structure that manages the files and their contents. It includes functions for reading, writing, and manipulating the data.
- Data point or Data set: Refer to a parent and a child relationship between the hierarchy of data. E.g. Data point: subgroup, Data set: group.

Example Usage:
- User data storage
- Game save files
- Configuration files
- Storing stats of entities
"""
from typing_extensions import TypeAlias
from os import walk, getcwd, path

__all__ = [
    'new_group',
    'new_data',
    'new_subgroup',
    'save',
    'update_data',
    'update_group',
    'update_subgroup'
]

DATA_WRAPPERS:dict[type|None, str] = {
    str: ['"', '"'],
    int: ['#', '#'],
    float: ['~', '~'],
    list: ['[', ']'],
    dict: ['{', '}'],
    tuple: ['(', ')'],
    bool: ['?', '?'],
    None: ['.', '.'],
    "settings": ['<', '>'],
    "group": ['*', '*'],
    "subgroup": [':', ':'],
    "item": ['|', '|'],
    "ignore": ['!', '!']
}

_Data: TypeAlias = str|int|float|list|dict|tuple|bool

class FileReadOnly(Exception):
    """Exception raised when trying to write to a read-only file."""
    def __init__(self, message="File is set to read-only."):
        self.message = message
        super().__init__(self.message)

class FileParsingError(Exception):
    """Exception raised when there is an error parsing the file."""
    def __init__(self, message="Error parsing file."):
        self.message = message
        super().__init__(self.message)

def _check_string_for_wrappers(data:str, check_for_type:str|type|None) -> bool:
    """Checks if the string data starts and ends with the correct wrappers."""
    if data.startswith(DATA_WRAPPERS[check_for_type][0]) and data.endswith(DATA_WRAPPERS[check_for_type][1]):
        return True
    return False

def file_search():
    """Searches for text files in the current directory and its subdirectories, setting the save file to the first one found."""
    all_text_files = []
    for root, _, files in walk(getcwd()):
        for file in files:
            if file.endswith('.txt'):
                with open(path.join(root, file), 'r') as f:
                    contents = f.read()
                if contents.startswith('!SAVE'):
                    return path.join(root, file)
                else:
                    all_text_files.append(path.join(root, file))

    if all_text_files:
        return path.join(root, file)
    else:
        print("WARNING: No text file found in the current directory or subdirectories.")
        return ""

def get_file_contents(filename:str) -> list[str]:
        """Gets the contents of the specified file."""
        with open(filename, 'r') as file:
            contents = file.read()
        contents = contents.splitlines()
        return contents

def split_iterables(data: _Data) -> list[str]:
    """Splits data into a list of strings, while keeping track of nesting."""
    iterables_prefixes = (DATA_WRAPPERS[list], DATA_WRAPPERS[dict], DATA_WRAPPERS[tuple])
    lists, dicts, tuples = 0, 0, 0
    last_sep = 0
    split_iterable = []
    for i in range(len(data)):
        char = data[i]
        if char == iterables_prefixes[0][0]: lists += 1
        elif char == iterables_prefixes[1][0]: dicts += 1
        elif char == iterables_prefixes[2][0]: tuples += 1
        elif char == iterables_prefixes[0][1]: lists -= 1
        elif char == iterables_prefixes[1][1]: dicts -= 1
        elif char == iterables_prefixes[2][1]: tuples -= 1
        elif char == "," and lists == 0 and dicts == 0 and tuples == 0:
            split_iterable.append(data[last_sep:i].strip())
            last_sep = i + 1
    return split_iterable + [data[last_sep:].strip()]

def convert_data_by_prefix(data:str) -> _Data:
    """Recursively converts prefixed string data to its appropriate type."""
    if _check_string_for_wrappers(data, str):
        return data[1:-1]
    elif _check_string_for_wrappers(data, int):
        return int(data[1:-1])
    elif _check_string_for_wrappers(data, float):
        return float(data[1:-1])
    elif _check_string_for_wrappers(data, bool):
        return data[1:-1].lower() == 'true'
    elif _check_string_for_wrappers(data, None):
        return None
    elif _check_string_for_wrappers(data, list):
        data = split_iterables(data[1:-1])
        return list([convert_data_by_prefix(item) for item in data])
    elif _check_string_for_wrappers(data, dict):
        data = split_iterables(data[1:-1])
        return {
            convert_data_by_prefix(key): convert_data_by_prefix(value) 
            for key, value in zip(data[0::2], data[1::2])
        } # Handles nested dictionaries recursively
    elif _check_string_for_wrappers(data, tuple):
        data = split_iterables(data[1:-1])
        return tuple(convert_data_by_prefix(item) for item in data)
    else:
        raise FileParsingError(f"Data '{data}' does not have a valid prefix or is in an incorrect format.")

class FileSaveSystem:
    """File save system for storing and manipulating data in a text file."""
    def __init__(self, filename:str, system_type:str = "read-write"):
        self.filename = filename
        self.system_type = system_type
        self.data = self.load()[0]
    def __str__(self):
        """Returns a string representation of the file save system."""
        return f"FileSaveSystem(filename={self.filename}, system_type={self.system_type}, data={self.data})"

    def load(self) -> dict[str, dict[str, dict[str, _Data]]]:
        """Gets all the data in the save file and outputs it as a dictionary."""
        contents = get_file_contents(self.filename)
        data:dict[str, dict[str, dict[str, list]]] = {} # first dict is the group and the second is the data blocks
        settings_string = ""
        current_group = None
        current_subgroup = None
        for line in contents:
                line = line.strip()
                if _check_string_for_wrappers(line, "ignore"):
                    continue
                if _check_string_for_wrappers(line, "settings"):
                    settings_string = line[1:-1]
                elif _check_string_for_wrappers(line, "group"):
                    current_group = line[1:-1]
                    data[current_group] = {}
                elif _check_string_for_wrappers(line, "subgroup"):
                    current_subgroup = line[1:-1]
                    data[current_group][current_subgroup] = {}
                elif _check_string_for_wrappers(line, "item"):
                    if current_group is None:
                        raise FileParsingError(f"Group not found or in incorrect format: {line}")
                    if current_subgroup is None:
                        raise FileParsingError(f"Subgroup not found or in incorrect format: {line}")
                    else:
                        item = line[1:-1]
                        try:
                            item, stored_data = item.split(":")
                        except ValueError:
                            raise FileParsingError(f"Item in incorrect format: {line}")
                        item = convert_data_by_prefix(item.strip())
                        stored_data = convert_data_by_prefix(stored_data.strip())
                        data[current_group][current_subgroup][item] = stored_data

        return (data, settings_string)
    def save(self):
        """Updates the contents of the specified file."""
        if self.system_type == 'read-only':
            raise FileReadOnly

    def content(self, group_name:str|int = None, subgroup_name:str|int = None, item_name:str|int = None) -> list[str]|_Data:
        """Gets the contents of the specified data set.

        - If `group_name`, `subgroup_name`, or `data_name` is `None`, the function returns a list of available names at the corresponding level.
        - If an integer is provided for any of these parameters, it is treated as an index in the respective list.
        - Index-based retrieval assumes valid indices; out-of-range values may lead to errors.
        """
        if group_name == None:
            return list(self.data.keys())
        if type(group_name) == int:
            group_name = list(self.data.keys())[group_name]
        if subgroup_name == None:
            return list(self.data[group_name].keys())
        if type(subgroup_name) == int:
            subgroup_name = list(self.data[group_name].keys())[subgroup_name]
        if item_name == None:
            return list(self.data[group_name][subgroup_name].keys())
        if type(item_name) == int:
            item_name = list(self.data[group_name][subgroup_name].keys())[item_name]
        return self.data[group_name][subgroup_name][item_name]
    def file_content(self):
        """Gets the groups in the file."""
        return self.content()
    def group_content(self, group_name:str|int) -> list:
        """Gets the subgroups inside of the specified group.
        
        Passing an integer to `group_name` will check for the index position.
        """
        return self.content(group_name)
    def subgroup_content(self, group_name:str|int, subgroup_name:str|int) -> list:
        """Gets all the data inside of the specified subgroup.
        
        Passing an integer to either `group_name` or `subgroup_name` will check for the index position.
        """
        return self.content(group_name, subgroup_name)
    def item_content(self, group_name:str|int, subgroup_name:str|int, item_name:str|int) -> str:
        """Gets the item from a specified data block in the specified group.

        Passing an integer to either `group_name`, `subgroup_name` or `item_name` will check for the index position.
        """
        # use get group contents function and get data contents function
        return self.content(group_name, subgroup_name, item_name)

    def contains(self, name_to_check:str, group_name:str|int = None, subgroup_name:str|int = None, item_name:str|int = None) -> bool:
        """Checks if the specified data point exists inside of the data set specified.

        Uses the `content` method to retrieve the list of available entries.
        """
        content = self.content(group_name, subgroup_name, item_name)
        return name_to_check in content
    def file_contains(self, name_to_check:str) -> bool:
        """Checks if the group specified exists inside of the file.

        Uses the `content` method to retrieve the list of available entries.
        """
        return self.contains(name_to_check)
    def group_contains(self, name_to_check:str, group_name:str|int) -> bool:
        """Checks if the subgroup specified exists inside of the specified group.

        Uses the `content` method to retrieve the list of available entries.
        """
        return self.contains(name_to_check, group_name)
    def subgroup_contains(self, name_to_check:str, group_name:str|int, subgroup_name:str|int) -> bool:
        """Checks if the item specified exists inside of the specified subgroup.

        Uses the `content` method to retrieve the list of available entries.
        """
        return self.contains(name_to_check, group_name, subgroup_name)
    def item_contains(self, name_to_check:str, group_name:str|int, subgroup_name:str|int, item_name:str|int) -> bool:
        """Checks if the name specified exists inside of the specified item.

        Uses the `content` method to retrieve the list of available entries.
        """
        return self.contains(name_to_check, group_name, subgroup_name, item_name)

    def new(self, group_name:str, subgroup_name:str|int = None, item_name:str|int = None, data:_Data = None):
        """Creates a new data point in the specified group, subgroup, and item.
        Raises:
            ValueError: If a required group or subgroup name is missing.
        - If `subgroup_name` or `item_name` is not specified, it will create a new subgroup or item respectively.
        - Passing an integer to either `to_group` or `to_subgroup` will check for the index position.
        - If the data point already exists, it will overwrite the existing data.
        """
        if subgroup_name is None:
            self.data[group_name] = {}
        if type(subgroup_name) == int:
            subgroup_name = list(self.data[group_name].keys())[subgroup_name]
        if item_name is None:
            if group_name not in self.data:
                self.data[group_name] = {}
            self.data[group_name][subgroup_name] = {}
        if type(item_name) == int:
            item_name = list(self.data[group_name][subgroup_name].keys())[item_name]
        if data is None:
            self.data[group_name][subgroup_name][item_name] = None
        else:
            try:
                DATA_WRAPPERS[type(data)]
            except KeyError:
                raise TypeError(f"Unsupported data type: {type(data)}")
            self.data[group_name][subgroup_name][item_name] = data
    def new_group(self, group_name:str):
        """Creates a new group that can be used to retrieve following information."""
        self.new(group_name)
    def new_subgroup(self, subgroup_name:str, to_group:str|int):
        """Creates a new data block that stores types of data inside of it.

        Passing an integer to `to_group` will automatically detect for a group at that index position.
        """
        self.new(to_group, subgroup_name)
    def new_item(self, item_name:str, data:_Data, to_group:str|int, to_subgroup:str|int):
        """Adds new data and item into the specified subgroup.

        Supported data types: `str`, `int`, `float`, `list`, `dict`, `tuple`, `bool`
        """
        self.new(to_group, to_subgroup, item_name, data)

    def update(self, old_group:str|int, new_group:str, old_subgroup:str|int = None, new_subgroup:str = None, old_item:str|int = None, new_item:str|int = None, new_data:_Data = None):
        """Updates the specified data point to the new one.
        Raises:
            ValueError: If a required new group or subgroup name is missing.
            ValueError: If attempting to create a duplicate group, subgroup, or item.
            TypeError: If the provided new data type is unsupported.
        - Renames or moves the specified group, subgroup, or item within the data structure.
        - Converts integer indices to corresponding names where necessary.
        - Ensures structural integrity by preventing duplicate names.
        - If `new_data` is provided, updates the corresponding item with new content.
        """
        if type(old_group) == int:
            old_group = list(self.data.keys())[old_group]
        if old_subgroup is None:
            if new_group is None:
                raise ValueError("Cannot update group without specifying a new group name.")
            if new_group in self.data.keys():
                raise ValueError(f"Group '{new_group}' already exists. Cannot have duplicate group names.")
            self.data[new_group] = self.data.pop(old_group, {})
        if type(old_subgroup) == int:
            old_subgroup = list(self.data[old_group].keys())[old_subgroup]
        if old_item is None:
            if new_subgroup is None:
                raise ValueError("Cannot update subgroup without specifying a new subgroup name.")
            if new_subgroup in self.data[old_group].keys():
                raise ValueError(f"Subgroup '{new_subgroup}' already exists in group '{old_group}'. Cannot have duplicate subgroup names.")
            self.data[new_group][new_subgroup] = self.data[old_group].pop(old_subgroup, {})
        if type(old_item) == int:
            old_item = list(self.data[old_group][old_subgroup].keys())[old_item]
        if new_data is None:
            if new_item is None:
                raise ValueError("Cannot update item without specifying a new item name.")
            if new_item in self.data[new_group][new_subgroup].keys():
                raise ValueError(f"Item '{new_item}' already exists in subgroup '{new_subgroup}' of group '{new_group}'. Cannot have duplicate item names.")
            self.data[new_group][new_subgroup][new_item] = self.data[old_group][old_subgroup].pop(old_item, None)
        else:
            try:
                DATA_WRAPPERS[type(new_data)]
            except KeyError:
                raise TypeError(f"Unsupported data type: {type(new_data)}")
            self.data[new_group][new_subgroup][new_item] = new_data
    def update_group(self, old_group:str|int, new_group:str):
        """Updates the specified group to the new one."""
        self.update(old_group, new_group)
    def update_subgroup(self, in_group:str|int, old_subgroup:str|int, new_subgroup:str):
        """Updates the specified subgroup to the new one."""
        self.update(in_group, None, old_subgroup, new_subgroup)
    def update_item(self, in_group:str|int, in_subgroup:str|int, old_item:str|int, new_item:str|int):
        """Updates the specified item content to the new one."""
        self.update(in_group, None, in_subgroup, None, old_item, new_item)
    def update_data(self, in_group:str|int, in_subgroup:str|int, in_item:str|int, new_data:_Data):
        """Updates the specified data to the new one."""
        self.update(in_group, None, in_subgroup, None, in_item, None, new_data)
