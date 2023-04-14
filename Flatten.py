#General Parameters:
#data: a container
#path_type: When emptying out/flattening a dictionary, 
#           decide whether to use an enountered array's indexes("index") or values("value") as keys
#           in key value pairs(or 2-tuples if the top layer is a list-like container)

#flatten: Empty out nested containers of the same type as the outermost container into the outermost container
#Currying is required, meaning this function returns a function which then returns the result
#When a dictionary is passed, the returned function asks for path_type which defaults to tuple
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
#If the outermost layer is a list-like container, inner dictionary key-value pairs are emptied into it as 2-tuples
#if the outermost layer is a dictionary, inner list-like containers are put emptied into it as a key value pair of either:
#1. The index of the array and the value at that index(list_like_value_key="index")
#2. The value of the array at an index and the value True(list_like_value_key="value")
def atomize(data, list_like_value_key="index", path_type=tuple):
    #Setup
    is_dict = isinstance(data, dict)

    def dict_concat(visited, _data, _path): 
        visited[_path] = _data
    def other_concat(visited, _data, _path): 
        visited += type(visited)([_data])
    concat_method = dict_concat if is_dict else other_concat

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
    list_like_value_key_loop = list_like_value_key_index_loop
    conform = conform_index
    if list_like_value_key == "value":
        list_like_value_key_loop = list_like_value_key_value_loop
        conform = conform_value

    #Making the 1d container
    def atomize_dict(_data, visited, _path, from_list_like=False):
        if isinstance(_data, dict):
            for key, val in _data.items():
                atomize_dict(val, visited, _path+[key], from_list_like)
        elif not isinstance(_data, str):
            try: list_like_value_key_loop(atomize_dict, _data, visited, _path, True)
            except (AttributeError, TypeError):
                if from_list_like:
                    concat_method(visited, conform(_data), path_type(_path))
                else: concat_method(visited, _data, path_type(_path))
        elif from_list_like: 
            concat_method(visited, conform(_data), path_type(_path))
        else: concat_method(visited, _data, path_type(_path))
        return visited
    
    def atomize_list_like(_data, visited, _path, from_dict=False):
        if isinstance(_data, dict):
            for key, val in _data.items():
                atomize_list_like(val, visited, _path+[key], True)
        elif not isinstance(_data, str):
            try: list_like_value_key_loop(atomize_list_like, _data, 
                                          visited, _path, from_dict)
            except (AttributeError, TypeError):
                if from_dict:
                    concat_method(visited, (path_type(_path), conform(_data)), path_type(_path))
                else: concat_method(visited, _data, path_type(_path))
        elif from_dict: 
            concat_method(visited, (path_type(_path), conform(_data)), path_type(_path))
        else: concat_method(visited, _data, path_type(_path))
        return visited

    if is_dict:
        return atomize_dict(data, type(data)(), [])
    return atomize_list_like(data, type(data)(), [])
