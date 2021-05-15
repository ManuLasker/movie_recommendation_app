import typer
import os

from multiprocessing import cpu_count
from queue import Queue
from src.worker import DownloadWorker, save_all
from src.config import BASE_URL, FAIL_RESPONSE
from src.models import Movie
from tqdm.auto import tqdm
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
         number_threads: int = typer.Option(cpu_count(),
                                           help="number of threads"),
         init_id: int  = typer.Option(0,
                                      help="initial id to begin iteration")) -> None:
    # create a queue to commnucate with the worker thread
    queue = Queue()
    # crate worker threads
    for num_worker in range(number_threads):
        worker = DownloadWorker(queue)
        # Setting daemon to True will let the main thread exit even though the workers are blocking
        worker.daemon = True
        worker.start()
        
    # Put the tasks into the queue as a tuple
    # main bar
    last_id = Movie.request_last_movie(host=BASE_URL, api_key=api_key).id
    last_id = 50
    all_ids = range(init_id, last_id + 1)
    main_bar = tqdm(desc="Queuing movie id:",
                    total=len(all_ids),
                    position=0)
    # thread bar
    thread_bar = tqdm(desc="Downloading movie",
                      total=len(all_ids),
                      position=1,
                      leave=True)
    
    for _id in all_ids:
        queue.put((BASE_URL, _id, api_key, data_path, thread_bar))
        main_bar.set_postfix(movie_id=_id)
        main_bar.update()
    # causes the main thread to wait for the queue to finish processing all the tasks
    queue.join()
    # save all
    main_logger.info("saving all the data to {}".format(data_path))
    save_all(data_path)
    main_logger.info("process finished!")
        
if __name__ == "__main__":
    typer.run(main)