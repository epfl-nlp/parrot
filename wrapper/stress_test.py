from multiprocessing import Process
import time

import gpt_wrapper
from gpt_wrapper.chat import Chat

# gpt_wrapper.api_base = "http://localhost:5000"
gpt_wrapper.api_key = "a5a244d0-2f56-41d3-ac99-9e5efb0e4079"


def create_chat_and_ask(process_id):
    start = time.time()
    chat = Chat.create("Test Chat")
    message = chat.ask("Who won the world series in 2020?")
    end = time.time()
    print(f"Process {process_id}: {str(message).strip()}\nTook {end - start} seconds")


if __name__ == "__main__":  # confirms that the code is under main function
    procs = []

    # instantiating process with arguments
    for i in range(64):
        proc = Process(target=create_chat_and_ask, args=(i + 1,))
        procs.append(proc)
        proc.start()

    # complete the processes
    for proc in procs:
        proc.join()
