# -*- coding: utf-8 -*-
import os, json
from datetime import datetime
from party_bag import *
from datetime import datetime, timedelta
from dateutil.relativedelta import *
from os import path

#excep output
from pyexcel_xlsx import save_data

#need an ordered dict from collactions for excel output
try:
    from collections import OrderedDict
except ImportError:
    OrderedDict = dict

###
#docker stop uspto-status-dump; docker container rm uspto-status-dump; cd ~/developer/uspto-status-dump && git pull && docker build -t uspto-status-dump .  && docker run -t --mount type=bind,source=/root/developer/uspto-status-dump,target=/src -v /etc/timezone:/etc/timezone:ro --name uspto-status-dump uspto-status-dump:latest
###

def date_format (this_date):
    #quick cheater
    return this_date[0:10]
    
#init data sheet
application_data_sheet = []

#set headers
row=[]
#--------------- ADD TO ROWS ---------------
row.append("DOCKET NUMBER")
row.append("APP NO")
row.append("FILING DATE")
row.append("TYPE")
row.append("EXAMINER")
row.append("ART UNIT")
row.append("APPLICANT")
row.append("ATTORNEY")
row.append("INVENTORS")
row.append("CONF")
row.append("AIA STATUS")
row.append("TITLE")
row.append("STATUS")
row.append("STATUS DATE")
row.append("PRE-GRANT PUB NO")
row.append("PRE-GRANT PUB DATE")
row.append("PAT NO")
row.append("PAT DATE")
row.append("LAST TRANSACTION")
row.append("LAST TRANSACTION DATE")

#append to the sheet 
application_data_sheet.append(row)

#year range
year_range = [1900]
for x in range(1990, 2020):
    year_range.append(x)

#parse through files 
for year in year_range:
    json_path = '/src/data/' + str(year)+'.json'

    #should skip? 
    if not path.exists(json_path):
        print ("Skip:" + str(year))
        continue 

    #init row for excel
    with open(json_path) as json_file:
        data = json.load(json_file)

        #init
        docket_num = ""
        app_num = ""
        app_date = ""
        app_type = ""
        examiner_name = ""
        art_unit = ""
        applicant = ""
        attorney = ""
        conf_num = ""
        aia_flag = ""
        title = ""
        status = ""
        status_date = ""
        pgpub = ""
        pgpub_date = ""
        patpub = ""
        patpub_date = ""
        most_recent_tx = ""
        most_recent_tx_date = ""

        #get patent data
        patent_data = data["PatentData"]
        total = len(patent_data)

        #iterate through each application
        for index, application in enumerate(patent_data):
            row=[]

            #**********************************************************************
            #               intermediate data 
            #**********************************************************************

            #get the databags
            patent_case_metadata = application.get("patentCaseMetadata", None)
            prosecution_history_data_bag = application.get("prosecutionHistoryDataBag", None)
            patent_term_data = application.get("patentTermData", None)
            assignment_data_bag = application.get("assignmentDataBag", None)

            #**********************************************************************
            #               metadata 
            #**********************************************************************
            if patent_case_metadata is not None:

                app_date = patent_case_metadata.get("filingDate","").upper()
                app_type = patent_case_metadata.get("applicationTypeCategory","").upper()
                app_num = patent_case_metadata["applicationNumberText"]["value"].upper()
                title = patent_case_metadata["inventionTitle"]["content"][0].upper()
                conf_num = patent_case_metadata.get("applicationConfirmationNumber","").upper()
                docket_num = patent_case_metadata.get("applicantFileReference","")
                aia_flag = patent_case_metadata.get("firstInventorToFileIndicator","").upper()
                status = patent_case_metadata.get("applicationStatusCategory","").upper()
                status_date = patent_case_metadata.get("applicationStatusDate","")
                
                #may not be assigned until examiner is assigned
                try:
                    art_unit = patent_case_metadata["groupArtUnitNumber"]["value"]
                except:
                    pass

                #nonpubliation requests
                try:
                    pgpub = patent_case_metadata["patentPublicationIdentification"]["publicationNumber"]
                    pgpub_date = patent_case_metadata["patentPublicationIdentification"]["publicationDate"]
                except:
                    pass

                #since not all cases are published
                try:
                    patpub = patent_case_metadata["patentGrantIdentification"]["patentNumber"]
                    patpub_date = patent_case_metadata["patentGrantIdentification"]["grantDate"]
                except:
                    pass
                
                #>>> GET PARTY INFORMATION
                if "partyBag" in patent_case_metadata:
                    #get partbag object
                    party_bag = patent_case_metadata["partyBag"]
                    
                    #EXRACT OUR DATA
                    examiner_name = get_examiner_name(party_bag = party_bag)
                    applicant = get_applicant(party_bag = party_bag)
                    inventor_list = get_inventor_list(party_bag = party_bag)
                    attorney = get_attorney(party_bag = party_bag)

            #**********************************************************************
            #               prosection 
            #**********************************************************************
            most_recent_tx = ""
            most_recent_tx_date = ""

            if prosecution_history_data_bag is not None:
                #>>> GET PROSECTION DATA

                #get last event counted
                last_event_counted = {} 

                if "prosecutionHistoryData" in prosecution_history_data_bag:
                    #get partbag object
                    pros_bag = prosecution_history_data_bag["prosecutionHistoryData"]

                    #get most recent status
                    bag_item = pros_bag[0]

                    code = bag_item["eventCode"]
                    date = bag_item["eventDate"]
                        
                    current_date = datetime.strptime(date, '%Y-%m-%d')

                        #print this at the end of a run to add to database
                    description = bag_item["eventDescriptionText"]

                    most_recent_tx_date =  date
                    most_recent_tx = description


            #--------------- ADD TO ROWS ---------------
            row.append(docket_num)
            row.append(app_num)
            row.append(date_format(app_date))
            row.append(app_type)
            row.append(examiner_name)
            row.append(art_unit)
            row.append(applicant)
            row.append(attorney)
            row.append("; ".join(inventor_list))
            row.append(conf_num)
            row.append(aia_flag)
            row.append(title)
            row.append(status)
            row.append(date_format(status_date))
            row.append(pgpub)
            row.append(date_format(pgpub_date))
            row.append(patpub)
            row.append(date_format(patpub_date))
            row.append(most_recent_tx)
            row.append(date_format(most_recent_tx_date))

            #append to the sheet 
            application_data_sheet.append(row)


print ("Making sheet...")

#manage excel data
excel_data = OrderedDict() # from collections import OrderedDict

#sheet name, along with row data
excel_data.update({ "Status Data Dump" : application_data_sheet})

print ("Saving sheet...")
#string io proxy for writing to memory
save_data("/src/data/status_dump.xlsx", excel_data)

print ("end")
