from typing import Any, Dict
import requests  as rq
import json

class Movie:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    @classmethod
    def request_movie_by_id(cls, host:str, api_key:str, _id:int):
        url = host + "/3/movie/" + str(_id)
        movie_data = cls.make_request(method="GET", url=url, api_key=api_key)
        return cls(**movie_data)
    
    @classmethod
    def request_last_movie(cls, host:str, api_key:str):
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