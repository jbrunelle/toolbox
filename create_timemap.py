from bs4 import BeautifulSoup
from urllib.parse import urlparse
import urllib.request
import sys
import argparse
from pathlib import Path
import json
import csv

parser = argparse.ArgumentParser(description='Create a CSV of mementos and archive datetimes')
parser.add_argument('uri',
                   help='single URI-R to process')
parser.add_argument('outfile',
                   help='file in which results are written')

args = parser.parse_args()

if(args.uri):
   print ("timemapping URI-R: %s" % args.uri)
else:
   parser.print_help()
   sys.exit()

   

########functions block#############



def readURIRs(fileLoc):
   retDict = {}
   with open(fileLoc) as f:
      retDict = f.read().splitlines()
   #print(retDict)
   return retDict
   
def uriValidator(u):
   try:
      result = urlparse(u)
      return True if [result.scheme, result.netloc, result.path] else False
   except:
      return False  
   
def getTimemap(u):
   mementos = {}
   urits={}
   ##get list of URI-Ts (URIs to timemaps)
   memURI = "http://labs.mementoweb.org/timemap/json/"+u
   req = urllib.request.Request(memURI)
   response = urllib.request.urlopen(req)
   timegates = response.read()
   utisjson = json.loads(timegates.decode("utf-8"))
   for t in utisjson["timemap_index"]:
      urits[t['from']]=t['uri']
      ##get all uri-ms from each uri-t
      req = urllib.request.Request(t['uri'])
      response = urllib.request.urlopen(req)
      timemap = response.read()
      tmjson = json.loads(timemap.decode("utf-8"))
      for m in tmjson["mementos"]['list']:  
         #2. create a dictionary of URI-Ms by datetime
         mementos[m['datetime']] = m['uri']
   return mementos

########END functions block#############   
   

myURIRs = {}

##read in the URI-R to process
if(args.uri):
   print("uri checking...")
   if(uriValidator(args.uri)):  #if valid URI-R
      print("valid uri...")
      myURIRs["cmd"] = args.uri
   else:
      print("Error with URI-R format!")
      sys.exit()
else:
   print("Error with URI-R initialization")
   sys.exit()

   
#for each URI-R...   
for urir in myURIRs:
   print("Creating: %s...\n" % myURIRs[urir])
   
   #retreive timemap of a URI-R
   myMementos = getTimemap(myURIRs[urir])
   #write results
   with open(args.outfile, 'w') as csv_file:
      writer = csv.writer(csv_file)
      for key, value in myMementos.items():
         writer.writerow([key, value])
   
print("\n\n Results written to ", args.outfile, "!\n\n")
