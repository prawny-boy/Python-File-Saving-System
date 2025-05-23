"""Manipulate text in files for saving, loading and reading."""
from typing_extensions import TypeAlias
import hashlib
from os import walk, getcwd, path

__all__ = [
    'new_header',
    'new_data',
    'new_data_block',
    'save',
    'update_data',
    'update_header',
    'update_data_block'
]

TYPE_PREFIXES:dict[type, str] = {
    str: '"',
    int: '#',
    float: '~',
    list: '&',
    dict: '%',
    tuple: '|',
    bool: '?'
}

_Data: TypeAlias = str|int|float|list|dict|tuple|bool

filename = "" # this is the file that will be used to save the data
only_read = False # if set to True, it will only read the file and not write to it, all writing functions will be disabled
data = "" # this is the variable that stores all the data in the file, it is a dictionary with the following format:
encoding = False # not implemented

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

# UTILITY FUNCTIONS ---------------------------------------------------------------

def _get_file_contents(filename:str) -> list[str]:
    """Gets the contents of the specified file."""
    with open(filename, 'r') as file:
        contents = file.read()
    contents = contents.splitlines()
    return contents

def _get_all_data() -> dict[str, dict[str, dict[str, _Data]]]:
    """Gets all the data in the save file and outputs it as a dictionary.

    Order Headers -> Data Blocks -> Data
    """
    contents = _get_file_contents(filename)
    data:dict[str, dict[str, dict[str, list]]] = {} # first dict is the header and the second is the data blocks
    current_header = None
    current_data_block = None
    for line in contents:
            if line.startswith('*') and line.endswith('*'):
                # header
                current_header = line[1:-1]
                data[current_header] = {}
            elif line.endswith(':'):
                # data block
                current_data_block = line[:-1]
                data[current_header][current_data_block] = {}
            else:
                # data
                if current_header is None:
                    raise FileParsingError(f"Header not found or in incorrect format: {line}")
                if current_data_block is None:
                    raise FileParsingError(f"Data block not found or in incorrect format: {line}")
                else:
                    split_data = line.split("|")
                    if len(split_data) < 2:
                        raise FileParsingError(f"Data in incorrect format: {line}")
                    data[current_header][current_data_block][split_data[0]] = split_data[1:]

    return data

def _update_data():
    """Updates the save_data variable using the save file."""
    global data
    data = _get_all_data()

def _update_file_contents(filename:str, contents:list[str]):
    """Updates the contents of the specified file."""
    if only_read == True:
        raise FileReadOnly
    with open(filename, 'w') as file:
        file.write('\n'.join(contents))

def _file_search():
    """Searches for text files in the current directory and its subdirectories, setting the save file to the first one found."""
    global filename
    for root, _, files in walk(getcwd()):
        for file in files:
            if file.endswith('.txt'):
                filename = path.join(root, file)
                return  # Exit once the first file is found

    if filename == "":
        print("WARNING: No text file found in the current directory or subdirectories.")

_file_search()
_update_data()

# READING FROM FILE ----------------------------------------------------------------------

def get_header_contents(header_name:str|int) -> list:
    """Gets the data blocks inside of the specified header.
    
    Passing an integer to `to_header` will check for the index position.
    """
    if type(header_name) == int:
        header_name = list(data.keys())[header_name]
    return list(data[header_name].keys())

def get_data_block_contents(header_name:str|int, data_block_name:str|int) -> list:
    """Gets all the data inside of the specified data block.
    
    Passing an integer to either `to_header` or `to_data_block` will check for the index position.
    """
    if type(header_name) == int:
        header_name = list(data.keys())[header_name]
    if type(data_block_name) == int:
        data_block_name = list(data[header_name].keys())[data_block_name]
    return list(data[header_name][data_block_name].keys())

def get_data_contents(header:str|int, data_block:str|int, data_name:str|int) -> str:
    """Gets the data from a specified data block in the specified header.

    Passing an integer to either `to_header`, `to_data_block` or `data_name` will check for the index position.
    """
    # use get header contents function and get data contents function
    if type(header) == int:
        header = list(data.keys())[header]
    if type(data_block) == int:
        data_block = list(data[header].keys())[data_block]
    if type(data_name) == int:
        data_name = list(data[header][data_block].keys())[data_name]
    return data[header][data_block][data_name]

# WRITING TO FILE ----------------------------------------------------------------------

def new_header(header_name:str):
    """Creates a new header that can be used to retrieve following information."""
    # headers are characterised with * at start and end
    # check for duplicate headers
    pass

def new_data_block(data_block_name:str, to_header:str|int):
    """Creates a new data block that stores types of data inside of it.

    Passing an integer to `to_header` will automatically detect for a header at that index position.
    """
    # data blocks are characterised with : at end
    # check for duplicates in a header
    # use get header contents function
    pass

def new_data(data:_Data, to_header:str|int, to_data_block:str|int):
    """Adds new data to the end of a specified data block in a header.
    
    Passing `None` to `to_header` will only add to the first data block with that name specified in `to_data_block`
    Passing an integer to either `to_header` or `to_data_block` will check for the index position.

    Supported data types: `str`, `int`, `float`, `list`, `dict`, `tuple`, `bool`
    """
    # use get header contents function and get data contents function
    # different types are characterised with different prefixes in the line shown by the type_prefixes constant
    try:
        prefix = TYPE_PREFIXES[type(data)]
    except KeyError:
        raise TypeError(f"Unsupported data type: {type(data)}")

def update_header(old_header:str|int, new_header:str):
    """Updates the specified header to the new one."""
    pass

def update_data_block(in_header:str|int, old_data_block:str|int, new_data_block:str):
    """Updates the specified data block to the new one."""
    pass

def update_data(in_header:str|int, in_data_block:str|int, old_data:str|int, new_data:_Data):
    """Updates the specified data to the new one."""
    pass

def save(filename:str):
    """Writes all the data into the specified file."""
    pass