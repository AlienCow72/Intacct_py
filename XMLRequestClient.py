import urllib.request
from xml.dom.minidom import parse

ENDPOINT_URL = "https://api.intacct.com/ia/xml/xmlgw.phtml"
TIMEOUT = 30

class XMLRequestClient:

    

    @staticmethod
    def post(request):
        # Set up the url Request class and use this Content Type
        # to avoid urlencoding everything
        header = {'Content-type': 'application/xml'}
        conn = urllib.request.Request(ENDPOINT_URL, headers = header, method='POST')

        # Post the request
        try:
            result = urllib.request.urlopen(conn, request.toxml(encoding="ascii"), TIMEOUT)
            print(result.getcode())
        except urllib.error.HTTPError as er:
            print("Error in XML R Client- HTTP ERROR")
            print(er)
            print(result.getcode())
            print(e)

        except urllib.error.URLError as e:
            print("Error in XML R Client- URL ERROR")
            print(result.getcode())
            print(e)


        # Check the HTTP code is 200-OK
        if result.getcode() != 200:
            # Log some of the info for debugging
            raise Exception("Received HTTP status code, " + result.getcode())

        # Load the XML into the response
        response = parse(result)
        return response

    def __init__(self):
        pass