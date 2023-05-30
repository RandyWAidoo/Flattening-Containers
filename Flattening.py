#General Parameters:
#data: an iterable
#path_type: A particular type.
#           When emptying out/flattening a dictionary, 
#           all keys traversed on the way down to a final, not-to-be-traversed, value are put together in a list 
#           which is then converted to an object of type path_type.
#           That path_type object will be the key of the value

#flatten: Empty out nested containers of the same type as the outermost container into the outermost container
#Currying is required, meaning this function returns a function which then returns the result
#When a dictionary is passed, the returned function asks for `path_type` which defaults to tuple
#Otherwise, the returned function has no parameters
def flatten(data):
    #Setup
    dtype = type(data)
    _visited = dtype()

    #Flattening
    def flatten_dict(_data, path_type, path, visited)->dict:
        if isinstance(_data, dtype):
            for key, val in _data.items():
                flatten_dict(val, path_type, path+[key], visited)
        else:
            visited[path_type(path)] = _data
        return visited
    
    def flatten_list_like(_data, visited)->dict:
        if isinstance(_data, dtype):
            for val in _data:
                flatten_list_like(val, visited)
        else:
            visited += dtype([_data])
        return visited

    if dtype == dict:
        def _flatten_dict(path_type=tuple):
            return flatten_dict(data, path_type, [], _visited)
        return _flatten_dict
    def _flatten_list_like(): return flatten_list_like(data, _visited)
    return _flatten_list_like

#atomize: Empty out all containers into the outermost container; make the container 1-dimesnsional
#If the outermost layer is a list-like container, 
# inner dictionary key-value pairs are emptied into it as 2-tuples
#if the outermost layer is a dictionary, 
# inner list-like containers are put emptied into it as a key value pair
#Parameter:
# list_like_value_key:
#  When adding to the list of traversed keys on the way to a value, 
#   different key options can be added when that value comes from with an array:
#  1. The current index of the array(list_like_value_key="index")
#  2. The value of the array at the current index(list_like_value_key="value"). 
#     When this happens, the corresponding value will be True
def atomize(data, list_like_value_key="index", path_type=tuple):
    #Setting function variables to be used later
    # Defining the functions
    def list_like_value_key_index_loop(func, _data, visited, _path, from_opposite):
        list_like_key = 0
        for val in _data:
            func(val, visited, _path+[list_like_key], from_opposite)
            list_like_key += 1
    def list_like_value_key_value_loop(func, _data, visited, _path, from_opposite):
        for val in _data:
            func(val, visited, _path+[val], from_opposite)
    def conform_index(_data): return _data
    def conform_value(_data): return True
    # Setting variables to them
    list_like_loop = list_like_value_key_index_loop
    conform = conform_index
    if list_like_value_key == "value":
        list_like_loop = list_like_value_key_value_loop
        conform = conform_value
    
    #Making the 1d container
    # atomimzing dictonaries
    def atomize_dict(_data, visited, _path, from_list_like=False):
        if isinstance(_data, dict):
            for key, val in _data.items():
                atomize_dict(val, visited, _path+[key], from_list_like)
        elif not isinstance(_data, str):
            try: list_like_loop(atomize_dict, _data, visited, _path, True)
            except (AttributeError, TypeError):
                if from_list_like:
                    visited[path_type(_path)] = conform(_data)
                else: visited[path_type(_path)] = _data
        elif from_list_like: 
            visited[path_type(_path)] = conform(_data)
        else: visited[path_type(_path)] = _data
        return visited
    
    # atomimzing list-like containers
    def atomize_list_like(_data, visited, _path, from_dict=False):
        if isinstance(_data, dict):
            for key, val in _data.items():
                atomize_list_like(val, visited, _path+[key], True)
        elif not isinstance(_data, str):
            try: list_like_loop(atomize_list_like, _data, 
                                visited, _path, from_dict)
            except (AttributeError, TypeError):
                if from_dict:
                    key = path_type(_path)
                    val = conform(_data)
                    visited += type(visited)((key, val))
                else: visited += type(visited)([_data])
        elif from_dict:
            key = path_type(_path)
            val = conform(_data)
            visited += type(visited)((key, val))
        else: visited += type(visited)([_data])
        return visited

    if isinstance(data, dict):
        return atomize_dict(data, type(data)(), [])
    return atomize_list_like(data, type(data)(), [])
