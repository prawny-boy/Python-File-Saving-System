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

TYPE_PREFIXES:dict[type|None, str] = {
    str: '"',
    int: '#',
    float: '~',
    list: '&',
    dict: '%',
    tuple: '|',
    bool: '?',
    None: '.'
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

class FileSaveSystem:
    """File save system for storing and manipulating data in a text file."""
    def __init__(self, filename:str, system_type:str = "read-write"):
        self.filename = filename
        self.system_type = system_type
        self.data = self.load()[0]

    def load(self) -> dict[str, dict[str, dict[str, _Data]]]:
        """Gets all the data in the save file and outputs it as a dictionary."""
        contents = get_file_contents(self.filename)
        data:dict[str, dict[str, dict[str, list]]] = {} # first dict is the group and the second is the data blocks
        settings_string = ""
        current_group = None
        current_subgroup = None
        for line in contents:
                line = line.strip()
                if line.startswith('!') or line == "":
                    # special cases
                    continue
                if (line.startswith('(') and line.endswith(')')):
                    # settings
                    settings_string = line[1:-1]
                elif line.startswith('*') and line.endswith('*'):
                    # group
                    current_group = line[1:-1]
                    data[current_group] = {}
                elif line.endswith(':'):
                    # data block
                    current_subgroup = line[:-1]
                    data[current_group][current_subgroup] = {}
                else:
                    # data
                    if current_group is None:
                        raise FileParsingError(f"group not found or in incorrect format: {line}")
                    if current_subgroup is None:
                        raise FileParsingError(f"Data block not found or in incorrect format: {line}")
                    else:
                        split_data = line.split("|")
                        if len(split_data) < 2:
                            raise FileParsingError(f"Data in incorrect format: {line}")
                        data[current_group][current_subgroup][split_data[0]] = split_data[1:]

        return (data, settings_string)
    def save(self):
        """Updates the contents of the specified file."""
        if self.system_type == 'read-only':
            raise FileReadOnly

    def content(self, group_name:str|int = None, subgroup_name:str|int = None, item_name:str|int = None) -> list[str]|_Data:
        """Gets the contents of the specified data set.

        Notes:
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

    def new(self, group_name:str, subgroup_name:str = None, item_name:str = None, data:_Data = None):
        """Creates a new data point in the specified group, subgroup, and item.
        
        If `subgroup_name` or `item_name` is not specified, it will create a new subgroup or item respectively.
        Passing an integer to either `to_group` or `to_subgroup` will check for the index position.
        """
        pass
    def new_group(self, group_name:str):
        """Creates a new group that can be used to retrieve following information."""
        pass
    def new_subgroup(self, subgroup_name:str, to_group:str|int):
        """Creates a new data block that stores types of data inside of it.

        Passing an integer to `to_group` will automatically detect for a group at that index position.
        """
        pass
    def new_item(self, item_name:str, data:_Data, to_group:str|int, to_subgroup:str|int):
        """Adds new data and item into the specified subgroup.

        Supported data types: `str`, `int`, `float`, `list`, `dict`, `tuple`, `bool`
        """
        try:
            prefix = TYPE_PREFIXES[type(data)]
        except KeyError:
            raise TypeError(f"Unsupported data type: {type(data)}")

    def update(self, old_group:str|int, new_group:str, old_subgroup:str|int = None, new_subgroup:str = None, old_item:str|int = None, new_item:str|int = None, new_data:_Data = None):
        """Updates the specified data point to the new one."""
        pass
    def update_group(self, old_group:str|int, new_group:str):
        """Updates the specified group to the new one."""
        pass
    def update_subgroup(self, in_group:str|int, old_subgroup:str|int, new_subgroup:str):
        """Updates the specified subgroup to the new one."""
        pass
    def update_item(self, in_group:str|int, in_subgroup:str|int, old_item:str|int, new_item:str|int):
        """Updates the specified item content to the new one."""
        pass
    def update_data(self, in_group:str|int, in_subgroup:str|int, in_item:str|int, new_data:_Data):
        """Updates the specified data to the new one."""
        pass
