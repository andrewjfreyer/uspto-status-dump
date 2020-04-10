import re

#--------------------------------------------------------
# EXAMINER NAME EXTRACT 
#--------------------------------------------------------
def get_examiner_name (party_bag):
    for item in party_bag["applicantBagOrInventorBagOrOwnerBag"]:
        if "primaryExaminerOrAssistantExaminerOrAuthorizedOfficer" in item:
            try:
                return item["primaryExaminerOrAssistantExaminerOrAuthorizedOfficer"][0]["name"]["personNameOrOrganizationNameOrEntityName"][0]["personFullName"]
            except:
                pass
    return ""

#--------------------------------------------------------
# GET APPLICANT
#--------------------------------------------------------
def get_applicant (party_bag):
    for item in party_bag["applicantBagOrInventorBagOrOwnerBag"]:
        if "applicant" in item:
            try:
                return item["applicant"][0]["contactOrPublicationContact"][0]["name"]["personNameOrOrganizationNameOrEntityName"][0]["organizationStandardName"]["content"][0].upper()
            except:
                pass
    return ""

#--------------------------------------------------------
# GET FIRM
#--------------------------------------------------------
def get_attorney (party_bag):
    for item in party_bag["applicantBagOrInventorBagOrOwnerBag"]:
        if "partyIdentifierOrContact" in item:
            try:
                name_of_rep = item["partyIdentifierOrContact"][0]["name"]["personNameOrOrganizationNameOrEntityName"][0]["personStructuredName"]["lastName"].upper()
                address_firstline = item["partyIdentifierOrContact"][0]["postalAddressBag"]["postalAddress"][0]["postalStructuredAddress"]["addressLineText"][0]["value"].upper()

                return name_of_rep + "/" + address_firstline
            except:
                pass
    return ""


#--------------------------------------------------------
# GET INVENTOR LIST
#--------------------------------------------------------
def get_inventor_list (party_bag):
    inventors = []
    for item in party_bag["applicantBagOrInventorBagOrOwnerBag"]:
        if "inventorOrDeceasedInventor" in item:
            for contact in item["inventorOrDeceasedInventor"]:
                if "contactOrPublicationContact" in contact:
                    contact_data = contact["contactOrPublicationContact"][0]

                    #name data
                    first_name = contact_data["name"]["personNameOrOrganizationNameOrEntityName"][0]['personStructuredName']["firstName"].upper()
                    middle_name = contact_data["name"]["personNameOrOrganizationNameOrEntityName"][0]['personStructuredName']["middleName"].upper()
                    last_name = contact_data["name"]["personNameOrOrganizationNameOrEntityName"][0]['personStructuredName']["lastName"].upper()

                    #combined name
                    name = first_name + " " + middle_name + " " + last_name

                    #append
                    inventors.append(re.sub(' +', ' ',name) )

    return inventors