# coding:utf-8
from cgi import print_arguments
from wsgiref.simple_server import make_server
import os
import time
 
# 定义函数，参数是函数的两个参数，都是python本身定义的，默认就行了。
def application(environ, start_response):
    if environ['REQUEST_METHOD'] == 'GET' and environ['PATH_INFO'] == '/latency':
        start_response('200 OK', [('Content-Type', 'text/html')])
        latency = str(getRequestTime())
        return [str.encode(latency)]

def getRequestTime():
    roundCount = 3
    start = time.time()
    for _ in range(roundCount):
        os.system("python3 client.py")
        # print(0)
    end = time.time()
    return (end - start) / roundCount
 
if __name__ == "__main__":
    port = 6088
    httpd = make_server("0.0.0.0", port , application)
    print("serving http on port {0}...".format(str(port)))
    httpd.serve_forever()
