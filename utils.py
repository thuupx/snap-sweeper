def chunkify(lst, chunk_size=20):
    for i in range(0, len(lst), chunk_size):
        yield lst[i : i + chunk_size]
