import typer
import time
import json
import os
from functools import reduce
# from log import main_logger, thread_logger
from models import Movie
from config import BASE_URL, FAIL_RESPONSE
from tqdm import tqdm

def get_id_in_filename(filename: str):
    _id = filename.split(".")[0].split("_")[-1]
    return int(_id)
    
def delete_not_used_files(data_path: str):
    files_paths = [os.path.join(data_path, name_file)
                   for name_file in os.listdir(data_path)]
    if len(files_paths) == 0: return
    max_id = reduce(lambda id_1, id_2: max(id_1, id_2),
                     map(get_id_in_filename, files_paths))
    for file in filter(lambda filename: get_id_in_filename(filename) < max_id,
                       files_paths):
        os.remove(file)
        
def directory_resolve_callback(data_path: str):
    if not os.path.exists(data_path):
        os.makedirs(data_path)
    return data_path

def main(api_key: str = typer.Argument(...,
                                       help="tmdb api_key for the user"),
         data_path: str = typer.Option("data",
                                       help="directory path where you want to save the data to.",
                                       callback=directory_resolve_callback)) -> None:
    """Downdload all the movies from tmdb and save it to a json file.
    """
    last_movie = Movie.request_last_movie(host=BASE_URL, api_key=api_key)
    movies = []
    for _id in tqdm(range(0, last_movie.id), desc="Downloading movies"):
        movie = Movie.request_movie_by_id(host=BASE_URL, api_key=api_key, _id=_id)
        
        try:
            movie_id = movie.id # not correct movie
        except Exception as error:
            assert movie.json() == FAIL_RESPONSE # supervise that is FAIL_RESPONSE
            continue
            
        movies.append(movie.json())
        if _id % 5 == 0:
            json.dump(movies, open(f"{data_path}/movie_data_{_id}.json", "w"),
                      indent=True)
            delete_not_used_files(data_path)
            time.sleep(10)

if __name__ == "__main__":
    typer.run(main)