# -*- coding: utf-8 -*-
import os, json
from datetime import datetime
from party_bag import *
from pros_bag import *
from datetime import datetime, timedelta
from dateutil.relativedelta import *

###
#docker stop uspto-status-dump; docker container rm uspto-status-dump; cd ~/developer/uspto-status-dump && git pull && docker build -t uspto-status-dump .  && docker run -t --mount type=bind,source=/root/developer/uspto-status-dump,target=/src -v /etc/timezone:/etc/timezone:ro --name uspto-status-dump uspto-status-dump:latest
###

def date_format (this_date):
    if not this_date is None and len(this_date) > 5:
        return datetime.strptime(this_date,'%Y-%m-%d')
    return ""

#parse through files 
for year in range(1900, 2050):
    with open('/src/data/' + str(year)+'.json') as json_file:
            data = json.load(json_file)

            #get patent data
            patent_data = data["PatentData"]
            total = len(patent_data)

            #iterate through each application
            for index, application in enumerate(patent_data):
                #establish the row
                row=[]

                #**********************************************************************
                #               intermediate data 
                #**********************************************************************

                #calculate progress
                progress = str(int((index + 1) / total * 100))

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
                if prosecution_history_data_bag is not None:
                    #>>> GET PROSECTION DATA

                    #get last event counted
                    last_event_counted = {} 

                    if "prosecutionHistoryData" in prosecution_history_data_bag:
                        #get partbag object
                        pros_bag = prosecution_history_data_bag["prosecutionHistoryData"]

                        #iterate through all of these items in chronological order
                        for bag_item in reversed(pros_bag):
                           
                            #get the codes from our bag_item
                            code = bag_item["eventCode"]
                            date = bag_item["eventDate"]
                            
                            current_date = datetime.strptime(date, '%Y-%m-%d')

                            #print this at the end of a run to add to database
                            add_line= "\"" + code + "\" : [ \"" + bag_item["eventDescriptionText"] + ", False]\","

                #--------------- ADD TO ROWS ---------------
                print(app_num)
                print(docket_num)
                print(datetime.strptime(app_date,'%Y-%m-%d'))
                print(app_date[0:4])
                print(app_type)
                print(examiner_name)
                print(art_unit)
                print(applicant)
                print(attorney)
                print("; ".join(inventor_list))
                print(len(inventor_list))
                print(conf_num)
                print(aia_flag)
                print(title)
                print(status)
                print(date_format(status_date))
                print(status_date[0:4])
                print(pgpub)
                print(date_format(pgpub_date))
                print(patpub)
                print(date_format(patpub_date))

