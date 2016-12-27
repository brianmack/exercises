import logging
import sys


def stream(f):
    """ Generic stream generator for files and streams.
    Implements readline powers for byte streams.  
    Follows iterator protocol, raising StopIteration 
    when exhausted, as at EOF for normal files.
    Inputs:
        f: object with 'read' method supporting 
            nbytes argument.
    Returns:
        lines from bytestream
    """
    chunk = ""
    while True:
        c = f.read(1)
        if c == "\n":
            yield chunk
            chunk = ""
            continue
        if c == "": # EOF
            if len(chunk):
                yield chunk
            raise StopIteration()
        chunk += c


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    while True:
        try:
            logging.info(stream(sys.stdin).next())
        except StopIteration:
            break

