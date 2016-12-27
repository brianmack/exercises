
import json
import multiprocess as mp
import SocketServer
import select
import struct
from threading import Thread



class RecordStreamer(SocketServer.StreamRequestHandler):
    """ Implements a simple record streamer, with data
    serialized as json."""


    def stream(self):
        
        while True:
            chunk = self.connection.recv(4)
            if len(chunk) < 4:
                break
            slen = struct.unpack(">L", chunk)[0]
            chunk = self.connection.recv(slen)
            while len(chunk) < slen:
                chunk += self.connection.recv(slen - len(chunk))
            obj = self.unpack(chunk)
            yield obj

    def unpack(self, data):
        return json.loads(data)
    


class RecordServer(SocketServer.ThreadingTCPServer):
    
    allow_reuse_address = 1

    def __init__(self, host="localhost", port=22):
        
        SocketServer.ThreadingTCPServer.__init__(self, (host, port), handler)
        self.abort = 0
        self.timeout = 1

    def serve_until_stopped(self):
        abort = 0
        while not abort:
            rd, wr, ex = select.select(
                [self.socket.fileno()], [], [], self.timeout)
            if rd:
                self.handle_request()
            abort = self.abort



def start_record_server():

    tcpserver = RecordServer()
    server_proc = mp.Process(
        target=tcpserver.serve_until_stopped)
    server_proc.start()
    return server_proc



if __name__ == "__main__":
    
    start_record_server()
