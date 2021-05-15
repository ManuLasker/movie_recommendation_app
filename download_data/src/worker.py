from threading import Thread
from queue import Queue
from src.models import Movie, MovieListJson
from src.log import thread_logger
# from tqdm import tqdm
movie_list = MovieListJson()
bad_request_movie = 0

class DownloadWorker(Thread):
    def __init__(self, queue: Queue):
        Thread.__init__(self)
        self.queue = queue
        
    def run(self):
        global bad_request_movie
        while True:
            host, _id, api_key, data_path, thread_bar = self.queue.get()
            thread_bar.set_postfix(movie_id=_id, thread_name=self.getName(), bad_movies=bad_request_movie)
            thread_bar.update()
            try:
                movie = Movie.request_movie_by_id(host=host, _id=_id, api_key=api_key)
                if getattr(movie, "id", None):
                    movie_list.append(movie.json())
                    movie_list.save(data_path)
                else:
                    bad_request_movie += 1
            finally:
                self.queue.task_done()