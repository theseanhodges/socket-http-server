import mimetypes
import re
import socket
import sys
import traceback
from pathlib import Path

WEBROOT = "webroot"

def response_ok(body=b"This is a minimal response", mimetype=b"text/plain"):
    """
    returns a basic HTTP response
    Ex:
        response_ok(
            b"<html><h1>Welcome:</h1></html>",
            b"text/html"
        ) ->

        b'''
        HTTP/1.1 200 OK\r\n
        Content-Type: text/html\r\n
        \r\n
        <html><h1>Welcome:</h1></html>\r\n
        '''
    """

    try:
        return b"""
HTTP/1.1 200 OK
Content-Type: """ + mimetype + b"""

""" + body + b"""
"""
    except TypeError:
        return b"""
HTTP/1.1 500 INTERNAL SERVER ERROR
Content-Type: text/html

<title>500 Internal Server Error</title>
<h1>Internal Server Error</h1>
<p>The server encountered an error and could not complete your request.</p>
"""

def response_method_not_allowed():
    """Returns a 405 Method Not Allowed response"""

    return b"""
HTTP/1.1 405 METHOD NOT ALLOWED
Content-Type: text/html

<title>405 Method Not Allowed</title>
<h1>Method Not Allowed</h1>
<p>The method is not allowed for the requested URL.</p>
"""


def response_not_found():
    """Returns a 404 Not Found response"""

    # TODO: Implement response_not_found
    return b""


def parse_request(request):
    """
    Given the content of an HTTP request, returns the path of that request.

    This server only handles GET requests, so this method shall raise a
    NotImplementedError if the method of the request is not GET.
    """

    match = re.match(r"([^\s]+) ([^\s]+) ([^\s]+)", request)
    if match:
        if match.group(1) == "GET":
            return match.group(2)
    raise NotImplementedError
    

def response_path(path):
    """
    This method should return appropriate content and a mime type.

    If the requested path is a directory, then the content should be a
    plain-text listing of the contents with mimetype `text/plain`.

    If the path is a file, it should return the contents of that file
    and its correct mimetype.

    If the path does not map to a real location, it should raise an
    exception that the server can catch to return a 404 response.

    Ex:
        response_path('/a_web_page.html') -> (b"<html><h1>North Carolina...",
                                            b"text/html")

        response_path('/images/sample_1.png')
                        -> (b"A12BCF...",  # contents of sample_1.png
                            b"image/png")

        response_path('/') -> (b"images/, a_web_page.html, make_type.py,...",
                             b"text/plain")

        response_path('/a_page_that_doesnt_exist.html') -> Raises a NameError

    """

    file = Path(WEBROOT + path)
    if file.is_dir():
        content = b"not implemented"
        mime_type = b"text/plain"
    elif file.is_file():
        content = file.read_bytes()
        mime_type = mimetypes.guess_type(file)[0].encode()
    else:
        raise NameError

    return content, mime_type


def server(log_buffer=sys.stderr):
    address = ('127.0.0.1', 10000)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print("making a server on {0}:{1}".format(*address), file=log_buffer)
    sock.bind(address)
    sock.listen(1)

    try:
        while True:
            print('waiting for a connection', file=log_buffer)
            conn, addr = sock.accept()  # blocking
            try:
                print('connection - {0}:{1}'.format(*addr), file=log_buffer)

                request = ''
                while True:
                    data = conn.recv(1024)
                    request += data.decode('utf8')

                    if '\r\n\r\n' in request:
                        break
		

                print("Request received:\n{}\n\n".format(request))

                try:
                    content, mime_type = response_path(parse_request(request))
                    response = response_ok(
                        body=content,
                        mimetype=mime_type
                    )
                except NotImplementedError:
                    response = response_method_not_allowed()
                except NameError:
                    response = response_not_found()

                conn.sendall(response)
            except:
                traceback.print_exc()
            finally:
                conn.close() 

    except KeyboardInterrupt:
        sock.close()
        return
    except:
        traceback.print_exc()


if __name__ == '__main__':
    server()
    sys.exit(0)


