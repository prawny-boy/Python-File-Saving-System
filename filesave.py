"""Manipulate text in files for saving and loading."""
from typing_extensions import TypeAlias
import hashlib

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

# # Example data to hash
# data = "Hello, world!"

# # Generate a SHA-256 hash
# hashed_value = hashlib.sha256(data.encode()).hexdigest()

# print("Original data:", data)
# print("Hashed value:", hashed_value)

_Data: TypeAlias = str|int|float|list|dict|tuple|bool

def _get_all_data() -> dict[str, dict[str, list]]:
    """Gets all the data in the save file and outputs it as a dictionary.

    Headers: Data Blocks: Data
    """
    pass

save_data:dict[str, dict[str, list]] = _get_all_data()

def _write_to_file(string:str,filename:str, line:int, insert:bool=True):
    """Writes to the specified file at the specified line
    
    If `insert` is set to `True` it will insert a new line into the file, otherwise it will override the line specified.
    """
    with open(filename, 'w') as file:
        contents = file.readlines()
        if insert:
            contents.insert(line, string)
        else:
            contents[line] = string
        file.writelines(contents)
    

def _get_header_contents(header_name:str|int) -> list:
    """Gets the data blocks inside of the specified header."""
    pass

def _get_data_block_contents(data_block_name:str|int) -> list:
    """Gets the data inside of the specified data block."""
    pass

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

def get_data(header:str|int, data_block:str|int) -> list:
    """Gets the data from a specified data block in the specified header.

    Passing `None` to `to_header` will only add to the first data block with that name specified in `to_data_block`
    Passing an integer to either `to_header` or `to_data_block` will check for the index position.
    """
    # use get header contents function and get data contents function
    pass

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