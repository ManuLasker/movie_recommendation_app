import typer
import os
from queue import Queue
from src.worker import DownloadWorker
from src.config import BASE_URL, FAIL_RESPONSE
from src.models import Movie

from tqdm import tqdm
from src.log import main_logger

        
def directory_resolve_callback(data_path: str) -> str:
    """Create directory path if it doesn't exist.

    Args:
        data_path (str): string data path

    Returns:
        [str]: string data path validated
    """
    if not os.path.exists(data_path):
        os.makedirs(data_path)
    return data_path

def main(api_key: str = typer.Argument(...,
                                       help="tmdb api_key for the user"),
         data_path: str = typer.Option("data",
                                       help="directory path where you want to save the data to.",
                                       callback=directory_resolve_callback),
         total: int = typer.Option(200000,
                                   help="number of movies you want to download")) -> None:
    # create a queue to commnucate with the worker thread
    queue = Queue()
    # crate 4 worker threads
    for num_worker in range(4):
        worker = DownloadWorker(queue)
        # Setting daemon to True will let the main thread exit even though the workers are blocking
        worker.daemon = True
        worker.start()
        
    # Put the tasks into the queue as a tuple
    # main bar
    main_bar = tqdm(desc="Queuing movie id:",
                    total=total,
                    position=0)
    # thread bar
    thread_bar = tqdm(desc="Downloading movie",
                      total=total,
                      position=1,
                      leave=True)
    
    for _id in range(0, Movie.request_last_movie(host=BASE_URL, api_key=api_key).id):
        queue.put((BASE_URL, _id, api_key, data_path, thread_bar))
        main_bar.set_postfix(movie_id=_id)
        main_bar.update()
    # causes the main thread to wait for the queue to finish processing all the tasks
    queue.join()
    main_logger.info("process finished!")
        
if __name__ == "__main__":
    typer.run(main)