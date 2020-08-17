''' By Kyle Anderson
    
    And set break points with this:
    import pytest; pytest.set_trace()


'''

from http.server import HTTPServer, BaseHTTPRequestHandler
import os
import xml
import json
import sys
import requests
import urllib.parse
from xml.dom.minidom import Document, parse
import XMLRequestClient
# from dotenv import load_dotenv

# import urllib.request
# import time
# load_dotenv()
# ITBridge_url = os.environ['URL']

senderId = "DSTaxMPP-DEV"
senderPassword = str('x%uTf@rcT&aG^9')

# sessionId = "mySessionId"

class sageServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("ok", "utf-8"))
        print('ok')

    def do_POST(self):
        
        try:
            #read post data
            postData = self.rfile.read(int(self.headers.get('content-length'))).decode()
            args=urllib.parse.parse_qs(postData)
            
            taxAmount = getTax(args)
            print("xXx")
            print("tax amount = " + taxAmount)
            print("xXx")
        except Exception as e:
            response = {'error': e.args[0]}
            print(response)
        finally:
            # print(url)
            # print(endpoint)
            self.send_response(200,"OK")

def getTax(args):
    # get strings out of args

    DOCtype = args.get('docType')#['docType']
    docType = DOCtype[0]
    
    sessionId = args['sessionId']
    SID = sessionId[0]

    DOCID = args['docId']
    docID = DOCID[0]
    QUERY=("DOCID= '" + docID + "'")


    try: # Write the XML request with the minidom  module
        newdoc = Document()
        ############## CONTROL ELEMENT #######################
        request = newdoc.createElement('request')
        newdoc.appendChild(request)
        control = newdoc.createElement('control')
        request.appendChild(control)
        senderid = newdoc.createElement('senderid')
        control.appendChild(senderid).appendChild(newdoc.createTextNode(senderId))
        senderpassword = newdoc.createElement('password')
        control.appendChild(senderpassword).appendChild(newdoc.createTextNode(senderPassword))
        controlid = newdoc.createElement('controlid')
        control.appendChild(controlid).appendChild(newdoc.createTextNode("testRequestId"))
        uniqueid = newdoc.createElement('uniqueid')
        control.appendChild(uniqueid).appendChild(newdoc.createTextNode("false"))
        dtdversion = newdoc.createElement('dtdversion')
        control.appendChild(dtdversion).appendChild(newdoc.createTextNode("3.0"))
        includewhitespace = newdoc.createElement('includewhitespace')
        control.appendChild(includewhitespace).appendChild(newdoc.createTextNode("false"))

        operation = newdoc.createElement('operation')
        request.appendChild(operation)

        ############### AUTHENTICATION ELEMENT ####################
        authentication = newdoc.createElement('authentication')
        operation.appendChild(authentication)

        sessionid = newdoc.createElement('sessionid')
        authentication.appendChild(sessionid).appendChild(newdoc.createTextNode(SID))

        ################ CONTENT ELEMENT ##########################
        content = newdoc.createElement('content')
        operation.appendChild(content)
        function = newdoc.createElement('function')
        content.appendChild(function).setAttributeNode(newdoc.createAttribute('controlid'))
        function.attributes["controlid"].value = "testFunctionId"

        queryFields = [
        'RECORDNO',
        'DOCNO',
        'DOCID',  # order number?
        'CUSTOMER.NAME',
        'CUSTOMER.CUSTOMERID',
        'BILLTO.MAILADDRESS.CITY',
        'BILLTO.MAILADDRESS.STATE',
        'BILLTO.MAILADDRESS.ZIP',
        'BILLTO.MAILADDRESS.COUNTRY',
        'BILLTO.MAILADDRESS.COUNTRYCODE',
        'SHIPTO.MAILADDRESS.CITY',
        'SHIPTO.MAILADDRESS.STATE',
        'SHIPTO.MAILADDRESS.ZIP',
        'SHIPTO.MAILADDRESS.COUNTRY',
        'SHIPTO.MAILADDRESS.COUNTRYCODE',
        'SUBTOTAL',
        'TOTAL']
 
        queryFields = "RECORDNO,DOCNO,DOCID,CUSTOMER.NAME,CUSTOMER.CUSTOMERID,BILLTO.MAILADDRESS.CITY,BILLTO.MAILADDRESS.STATE,BILLTO.MAILADDRESS.ZIP,BILLTO.MAILADDRESS.COUNTRY,BILLTO.MAILADDRESS.COUNTRYCODE,SHIPTO.MAILADDRESS.CITY,SHIPTO.MAILADDRESS.STATE,SHIPTO.MAILADDRESS.ZIP,SHIPTO.MAILADDRESS.COUNTRY,SHIPTO.MAILADDRESS.COUNTRYCODE,SUBTOTAL,TOTAL"
        
    # Sales Order Query
        if (docType == "Sales Order"):
            readByQuery = newdoc.createElement('readByQuery')
            function.appendChild(readByQuery)
            object = newdoc.createElement('object')
            readByQuery.appendChild(object).appendChild(newdoc.createTextNode("SODOCUMENT"))
            fields = newdoc.createElement('fields')
            readByQuery.appendChild(fields).appendChild(newdoc.createTextNode(queryFields))
            query = newdoc.createElement('query')
            readByQuery.appendChild(query).appendChild(newdoc.createTextNode(QUERY)) # All records
    # Purchase Order Query 
        if (docType == 'Purchase Order'):
            readByQuery = newdoc.createElement('readByQuery')
            function.appendChild(readByQuery)
            object = newdoc.createElement('object')
            readByQuery.appendChild(object).appendChild(newdoc.createTextNode("PODOCUMENT"))
            fields = newdoc.createElement('fields')
            readByQuery.appendChild(fields).appendChild(newdoc.createTextNode(queryFields))
            query = newdoc.createElement('query')
            readByQuery.appendChild(query).appendChild(newdoc.createTextNode(DOCID=docID))

        print(request.toprettyxml())

        # Post the request
        response = XMLRequestClient.XMLRequestClient.post(request)

    except Exception as inst:
        print("Uh oh, something is wrong in getTax()")
        print(type(inst))
        print(inst.args)
        print("end of getTax Error")

    # Print the XML response to the console
    print(response.toprettyxml())
    xml_data_array = response._get_documentElement('result')
    # prettyxml=xml_data_array
    print(xml_data_array)
    

    
    placehorder= "No Tax to return yet"
    return(placehorder)

    


def updateTaxAmount(taxAmount, args):
    pass

#############################################################################
#Main

# If Request Method is Get--Done
    # Print ok --Done

# If Request Method is Post-- DONE
    # Try
        # $args=$Post

        # $Config = newClientConfig

        # $taxAmount = getTax($config, $args)
    # Catch
        #$responce = Error


    #################################################
# function newClientConfig($args)
    # {
        # $config = new ClientConfig();
        # if (isset($args['endpoint'])) {
        #     $config->setEndpointUrl($args['endpoint']);
        # }
        # if (isset($args['sessionId'])) {
        #     $config->setSessionId($args['sessionId']);
        # }
        # return $config;
    # }


############################################################
# function getTax($config, $args)
    # get data from object (SO,PO,invoice)
    # pass to ITBridge



#############################################################
#function updateTaxAmount($taxAmount, $args, $config)

def main():
    PORT = 8000
    server_address= ('localhost',PORT)
    webServer=HTTPServer(server_address,sageServer)
    print('Server is running on port %s' %PORT)
    webServer.serve_forever()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass

    webServer.server_close()