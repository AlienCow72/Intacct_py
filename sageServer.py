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
import configparser
from xml.dom import minidom
from xml.dom.minidom import Document, parse
import xml.etree.ElementTree as ET
import XMLRequestClient

config=configparser.ConfigParser(interpolation=None)
config.read('credentials.ini')
ini=config['default']


senderId = ini.get('sender_id') 
senderPassword = ini.get('sender_password')
ITBridgeURL = ini.get('ITBridgeURL')
ITBridgeAPIKey = ini.get('ITBridgeAPIKey')

# testing
    # queryFields = [
    #         'RECORDNO',
    #         'DOCNO',
    #         'DOCID',  # order number?
    #         'CUSTOMER.NAME',
    #         'CUSTOMER.CUSTOMERID',
    #         'BILLTO.MAILADDRESS.CITY',
    #         'BILLTO.MAILADDRESS.STATE',
    #         'BILLTO.MAILADDRESS.ZIP',
    #         'BILLTO.MAILADDRESS.COUNTRY',
    #         'BILLTO.MAILADDRESS.COUNTRYCODE',
    #         'SHIPTO.MAILADDRESS.CITY',
    #         'SHIPTO.MAILADDRESS.STATE',
    #         'SHIPTO.MAILADDRESS.ZIP',
    #         'SHIPTO.MAILADDRESS.COUNTRY',
    #         'SHIPTO.MAILADDRESS.COUNTRYCODE',
    #         'SUBTOTAL',
    #         'TOTAL']

    # test='''<?xml version="1.0" ?><response><control><status>success</status><senderid>DSTaxMPP-DEV</senderid><controlid>testRequestId</controlid><uniqueid>false</uniqueid><dtdversion>3.0</dtdversion></control><operation><authentication><status>success</status><userid>Guest</userid><companyid>DSTaxMPP-DEV</companyid><locationid/><sessiontimestamp>2020-08-22T01:50:00+00:00</sessiontimestamp><sessiontimeout>2020-08-22T13:50:00+00:00</sessiontimeout></authentication><result><status>success</status><function>readByQuery</function><controlid>testFunctionId</controlid><data listtype="sodocument" count="1" totalcount="1" numremaining="0" resultId=""><sodocument><RECORDNO>645</RECORDNO><DOCNO>SO-0254</DOCNO><DOCID>Sales Order-SO-0254</DOCID><CUSTOMER.NAME>Mercado Sidewalk Cafe</CUSTOMER.NAME><CUSTOMER.CUSTOMERID>CUST-00106</CUSTOMER.CUSTOMERID><BILLTO.MAILADDRESS.CITY>Santa Clara</BILLTO.MAILADDRESS.CITY><BILLTO.MAILADDRESS.STATE>CA</BILLTO.MAILADDRESS.STATE><BILLTO.MAILADDRESS.ZIP>95054</BILLTO.MAILADDRESS.ZIP><BILLTO.MAILADDRESS.COUNTRY/><BILLTO.MAILADDRESS.COUNTRYCODE/><SHIPTO.MAILADDRESS.CITY>Santa Clara</SHIPTO.MAILADDRESS.CITY><SHIPTO.MAILADDRESS.STATE>CA</SHIPTO.MAILADDRESS.STATE><SHIPTO.MAILADDRESS.ZIP>95054</SHIPTO.MAILADDRESS.ZIP><SHIPTO.MAILADDRESS.COUNTRY/><SHIPTO.MAILADDRESS.COUNTRYCODE/><SUBTOTAL>349</SUBTOTAL><TOTAL>349</TOTAL></sodocument></data></result></operation></response>'''
    # mytree= ET.fromstring(test)

    # operation=mytree[1]
    # results=operation[1]
    # data=results[3]
    # potato=data[0]

    # # print(data[0].tag)

    # # for x in data[0]:
    # #     print(x.tag, x.text)

    # order={}
    # x=0
    # for field in queryFields:
    #     order[field]=potato[x].text
    #     x+=1

    # print(order)

        

    # print(order['RECORDNO'])

# testing 2
    # fields = [
    #         'RECORDNO',
    #         'ITEMID',
    #         'ITEMNAME',
    #         'QUANTITY',
    #         'PRICE',
    #         'TOTAL',
    #     ]

    # queryFields = ""

    # for field in fields:
    #     while field.
    #     <fields.count():
    #         queryFields += field +","
    #     queryFields += field
        

    # print(queryFields)


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
            
            # get tax amount by pulling order data from intacct, then passing to ITBridge, and recieving the value back 
            taxAmount = getTax(args)


            print("tax amount = " + taxAmount)
            
        except Exception as e:
            response = {'error in main': e.args}
            print(response)
        finally:
            # print(url)
            # print(endpoint)
            self.send_response(200,"OK")

def getTax(args):
   
    try: # get strings out of args
        DOCtype = args.get('docType')
        docType = DOCtype[0]
        
        sessionId = args['sessionId']
        SID = sessionId[0]

        DOCID = args['docId']
        docID = DOCID[0]
        OrderQUERY=("DOCID= '" + docID + "'")
        ItemQUERY=("DOCHDID= '" + docID + "'")
    except Exception as e:
        pass

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
 
        Fields = "RECORDNO,DOCNO,DOCID,CUSTOMER.NAME,CUSTOMER.CUSTOMERID,BILLTO.MAILADDRESS.CITY,BILLTO.MAILADDRESS.STATE,BILLTO.MAILADDRESS.ZIP,BILLTO.MAILADDRESS.COUNTRY,BILLTO.MAILADDRESS.COUNTRYCODE,SHIPTO.MAILADDRESS.CITY,SHIPTO.MAILADDRESS.STATE,SHIPTO.MAILADDRESS.ZIP,SHIPTO.MAILADDRESS.COUNTRY,SHIPTO.MAILADDRESS.COUNTRYCODE,SUBTOTAL,TOTAL"
        
    # Sales Order Query
        if (docType == "Sales Order"):
            readByQuery = newdoc.createElement('readByQuery')
            function.appendChild(readByQuery)
            object = newdoc.createElement('object')
            readByQuery.appendChild(object).appendChild(newdoc.createTextNode("SODOCUMENT"))
            fields = newdoc.createElement('fields')
            readByQuery.appendChild(fields).appendChild(newdoc.createTextNode(Fields))
            query = newdoc.createElement('query')
            readByQuery.appendChild(query).appendChild(newdoc.createTextNode(OrderQUERY)) # All records
    # Purchase Order Query 
        if (docType == 'Purchase Order'):
            readByQuery = newdoc.createElement('readByQuery')
            function.appendChild(readByQuery)
            object = newdoc.createElement('object')
            readByQuery.appendChild(object).appendChild(newdoc.createTextNode("PODOCUMENT"))
            fields = newdoc.createElement('fields')
            readByQuery.appendChild(fields).appendChild(newdoc.createTextNode(Fields))
            query = newdoc.createElement('query')
            readByQuery.appendChild(query).appendChild(newdoc.createTextNode(OrderQUERY))

        # print(request.toprettyxml())

        # Post the request
        response = XMLRequestClient.XMLRequestClient.post(request)

    except Exception as inst:
        print("\nUh oh, something is wrong in getTax()")
        print(type(inst))
        print(inst.args)
        print("end of getTax Error\n")

# convert responce data into readable format
    # print(response.toprettyxml())
    orderxml=response.toxml()
    mytree= ET.fromstring(orderxml)
    operation=mytree[1]
    results=operation[1]
    data=results[3]
    potato=data[0]
    print(potato)
#  Put order fields into an array
    # for x in data[0]:
    #     print(x.tag, x.text)
    try:
        order={}
        x=0
        for field in queryFields:
            order[field]=potato[x].text
            x+=1

    except Exception as inst:
        print("\nUh oh, something is wrong in order details()")
        print(type(inst))
        print(inst.args)
        print("end of getTax Error\n")
    
    print(order)


# Query for order items

    # queryFields = [
    #     'RECORDNO',
    #     'ITEMID',
    #     'ITEMNAME',
    #     'QUANTITY',
    #     'PRICE',
    #     'TOTAL',
    # ]

    # Fields = "RECORDNO,ITEMID,ITEMNAME,QUANTITY,PRICE,TOTAL"

    # try: # Write the XML request with the minidom  module
    #     newdoc = Document()
    #     ############## CONTROL ELEMENT #######################
    #     request = newdoc.createElement('request')
    #     newdoc.appendChild(request)
    #     control = newdoc.createElement('control')
    #     request.appendChild(control)
    #     senderid = newdoc.createElement('senderid')
    #     control.appendChild(senderid).appendChild(newdoc.createTextNode(senderId))
    #     senderpassword = newdoc.createElement('password')
    #     control.appendChild(senderpassword).appendChild(newdoc.createTextNode(senderPassword))
    #     controlid = newdoc.createElement('controlid')
    #     control.appendChild(controlid).appendChild(newdoc.createTextNode("testRequestId"))
    #     uniqueid = newdoc.createElement('uniqueid')
    #     control.appendChild(uniqueid).appendChild(newdoc.createTextNode("false"))
    #     dtdversion = newdoc.createElement('dtdversion')
    #     control.appendChild(dtdversion).appendChild(newdoc.createTextNode("3.0"))
    #     includewhitespace = newdoc.createElement('includewhitespace')
    #     control.appendChild(includewhitespace).appendChild(newdoc.createTextNode("false"))

    #     operation = newdoc.createElement('operation')
    #     request.appendChild(operation)

    #     ############### AUTHENTICATION ELEMENT ####################
    #     authentication = newdoc.createElement('authentication')
    #     operation.appendChild(authentication)

    #     sessionid = newdoc.createElement('sessionid')
    #     authentication.appendChild(sessionid).appendChild(newdoc.createTextNode(SID))

    #     ################ CONTENT ELEMENT ##########################
    #     content = newdoc.createElement('content')
    #     operation.appendChild(content)
    #     function = newdoc.createElement('function')
    #     content.appendChild(function).setAttributeNode(newdoc.createAttribute('controlid'))
    #     function.attributes["controlid"].value = "testFunctionId"
    # # Sales Order Query
    #     if (docType == "Sales Order"):
    #         readByQuery = newdoc.createElement('readByQuery')
    #         function.appendChild(readByQuery)
    #         object = newdoc.createElement('object')
    #         readByQuery.appendChild(object).appendChild(newdoc.createTextNode("SODOCUMENTENTRY"))
    #         fields = newdoc.createElement('fields')
    #         readByQuery.appendChild(fields).appendChild(newdoc.createTextNode(queryFields))
    #         query = newdoc.createElement('query')
    #         readByQuery.appendChild(query).appendChild(newdoc.createTextNode(ItemQUERY)) # All records
    # # Purchase Order Query 
    #     if (docType == 'Purchase Order'):
    #         readByQuery = newdoc.createElement('readByQuery')
    #         function.appendChild(readByQuery)
    #         object = newdoc.createElement('object')
    #         readByQuery.appendChild(object).appendChild(newdoc.createTextNode("PODOCUMENTENTRY"))
    #         fields = newdoc.createElement('fields')
    #         readByQuery.appendChild(fields).appendChild(newdoc.createTextNode(queryFields))
    #         query = newdoc.createElement('query')
    #         readByQuery.appendChild(query).appendChild(newdoc.createTextNode(ItemQUERY))
    
    # #send Request
    #     response = XMLRequestClient.XMLRequestClient.post(request)

    # except Exception as inst:
    #     print("\nUh oh, something is wrong in orderitems()")
    #     print(type(inst))
    #     print(inst.args)
    #     print("end of getTax Error\n")

    # print(response.toprettyxml)
    


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




# server variables
PORT = 8000
server_address= ('localhost',PORT)
webServer=HTTPServer(server_address,sageServer)

def main():
    
    print('Server is running on port %s' %PORT)
    webServer.serve_forever()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        webServer.server_close()
        print('\nServer Closed')