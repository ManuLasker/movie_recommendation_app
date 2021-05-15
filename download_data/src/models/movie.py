from typing import Any, Dict, List
from functools import reduce

import requests  as rq
import json
import os

def get_id_in_filename(filename: str) -> int:
    """get id from filename with name as following
    filename: /path/to/movie_data_{id}.json

    Args:
        filename (str): filename where is a part of the data

    Returns:
        [int]: id retrieved from filename
    """
    _id = filename.split(".")[0].split("_")[-1]
    return int(_id)
    
def delete_not_used_files(data_path: str):
    """delete not used files from data directory

    Args:
        data_path (str): data directory where the files are stored
    """
    files_paths = [os.path.join(data_path, name_file)
                   for name_file in os.listdir(data_path)]
    if len(files_paths) == 0: return
    max_id = reduce(lambda id_1, id_2: max(id_1, id_2),
                     map(get_id_in_filename, files_paths))
    for file in filter(lambda filename: get_id_in_filename(filename) < max_id,
                       files_paths):
        os.remove(file)
        
class Movie:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    @classmethod
    def request_movie_by_id(cls, host:str, api_key:str, _id:int) -> 'Movie':
        url = host + "/3/movie/" + str(_id)
        movie_data = cls.make_request(method="GET", url=url, api_key=api_key)
        return cls(**movie_data)
    
    @classmethod
    def request_last_movie(cls, host:str, api_key:str) -> 'Movie':
        url = host + "/3/movie/latest"
        movie_data = cls.make_request(method="GET", url=url, api_key=api_key)
        return cls(**movie_data)
    
    @staticmethod
    def make_request(method, url, **kwargs) -> Dict[str, Any]:
        if method == 'GET':
            try:
                return json.loads(rq.get(url=url, params=kwargs).text)
            except Exception as error:
                raise error
        raise NotImplementedError(f"Method {method} not supported!")
    
    def json(self)->Dict[str, Any]:
        return self.__dict__
    
    
class MovieListJson:
    def __init__(self):
        self.movies:List[Dict[str, Any]] = []
        
    def append(self, movie:Dict[str, Any]):
        self.movies.append(movie)
        
    def save(self, data_path:str):
        _id = self.get_last_movie_id()
        if  _id % 10 == 0:
            json.dump(self.movies,
                      open(os.path.join(data_path, f"movie_data_{_id}.json"), "w"),
                      indent=True)
            delete_not_used_files(data_path)
        
    def get_last_movie_id(self) -> int:
        return self.movies[-1]["id"]