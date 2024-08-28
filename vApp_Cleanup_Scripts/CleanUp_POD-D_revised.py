import sys
import re
import subprocess
import json
import xml.etree.ElementTree as ET
from operator import itemgetter

CURL = '/usr/bin/curl'
enmdrop_rest_api = 'https://ci-portal.seli.wh.rnd.internal.ericsson.com/dropsInProduct/.json/?products=ENM'


catalog_report_file='/var/tmp/catalog_report.xml'
catalog_to_cleanup = 'ENM-catalog-install'
#catalog_to_cleanup = 'DE-Oceans'
spp_api_to_fetch_catalog_templates = 'VappTemplates/index_api/catalog_name:'
spp_api_to_delete_template='VappTemplates/delete_api/vapp_template_id:'

pods = {'C' : 'https://atvpcspp12.athtem.eei.ericsson.se/', \
        'D' : 'https://atvpdspp13.athtem.eei.ericsson.se/', \
        'E' : 'https://atvpespp14.athtem.eei.ericsson.se/', \
        'G' : 'https://atvpgspp16.athtem.eei.ericsson.se/', \
        'H' : 'https://atvphspp17.athtem.eei.ericsson.se/', \
        'K' : 'https://atvpkspp20.athtem.eei.ericsson.se/'}

def get_valid_sprint_list():
    sprint_list = []

    get_drop_command = str(CURL) + ' ' + enmdrop_rest_api
    response = subprocess.Popen(get_drop_command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (available_drops, stderr) = response.communicate()
   
    drops_data = json.loads(available_drops)

    for num in range(0,4):
        sprint_list.append(str(drops_data['Drops'][num].split(':')[1]))
    return sprint_list

def get_valid_sprint_list2():
    sprint_list = []

    get_drop_command = str(CURL) + ' ' + enmdrop_rest_api
    response = subprocess.Popen(get_drop_command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (available_drops, stderr) = response.communicate()
    drops_data = json.loads(available_drops)
    for num in range(0,3):
        sprint_list.append(str(drops_data['Drops'][num].split(':')[1]))
    return sprint_list
	
def get_valid_sprint_list3():
    sprint_list = []

    get_drop_command = str(CURL) + ' ' + enmdrop_rest_api
    response = subprocess.Popen(get_drop_command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (available_drops, stderr) = response.communicate()
    drops_data = json.loads(available_drops)
    for num in range(0,4):
        sprint_list.append(str(drops_data['Drops'][num].split(':')[1]))
    return sprint_list
	
def get_valid_templates(sprint, pod, vapp_type, count):
    templates_map={}
    template_name = ''
    template_id = ''
    vapp = ''
    current_sprint = get_valid_sprint_list()[0]
    previous_sprint = get_valid_sprint_list()[1]
    

    command_to_get_catalog_report = str(CURL) + ' -u administrator:admin01 --insecure ' + pod + \
    str(spp_api_to_fetch_catalog_templates) + catalog_to_cleanup + '/.xml'

    response = subprocess.Popen(command_to_get_catalog_report.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (catalogs_list,stderr) = response.communicate()
    with open(catalog_report_file,'w') as file:
        file.write(catalogs_list)

    #print "Command: ", command_to_get_catalog_report
    if vapp_type == "SSGID" or vapp_type == "all" :
        vapp = ""
    elif vapp_type == "FULL":
        vapp = "_FULL"


    if sprint == "all":
        match_pattern="^ENM"+str(vapp)+"_Ready_*"
        #print "Match Pattern: ", match_pattern
    else:
        match_pattern="^ENM"+str(vapp)+"_Ready_"+sprint+"_*"
        #print "Match Pattern: ", match_pattern

    tree = ET.parse(catalog_report_file)
    root = tree.getroot()

    
    for item in root:
        if item.tag == 'vapptemplates':
            #temp_map=[]
            for subitem in item:
                if subitem.tag == 'vapptemplate_name':
                    #print "vapptemplate_name: ", subitem.text
                    template_name = subitem.text
                if subitem.tag == 'vapptemplate_id':
                    #print "vapptemplate_ID: ", subitem.text
                    template_id = subitem.text
            if re.match(match_pattern, template_name):
                if sprint == "all":
                    templates_map[template_name]=template_id
                else:
                    if len(templates_map) < count:
                        templates_map[template_name]=template_id
    
    return templates_map

def main (argv):
#    valid_enm_vapp_template_dict = {}
#    enm_vapp_template_delete_dict={}
    sprint_list = []
    sprint_list1 = get_valid_sprint_list()
    sprint_list2 = get_valid_sprint_list2()
    sprint_list3 = get_valid_sprint_list3()

    for pod in ['C', 'D', 'E', 'G', 'H', 'K']:
        print "\n\n\n\n=================================="
        print "|             POD: "+pod+"             |"
        print "----------------------------------"
        for type in ["SSGID", "FULL"]:
            enm_vapp_template_delete_dict={}
            valid_enm_vapp_template_dict = {}


            all_enm_vapp_template_dict = get_valid_templates("all", pods[pod], type, count=None) #all
            print "All "+type+" templates"
            for key in sorted(all_enm_vapp_template_dict.keys(), reverse=1):
             # print  str(key)+" : "+str(all_enm_vapp_template_dict[key])
		print str(key)+":"+str(all_enm_vapp_template_dict[key])
            print "------"
            if pod == "D":
               sprint_list = sprint_list2
               print "Valid sprints", sprint_list2
            elif pod == "G" or pod == "E":
               sprint_list = sprint_list3
               print "Valid sprints", sprint_list3
	    else:
               sprint_list = sprint_list1
               print "Valid sprints", sprint_list1
            '''
            for sprint in sprint_list:
    #            print "Sprint: "+str(sprint)+"\n"+"================="+"\n"
                vapp_template_dict = get_valid_templates(sprint, pods[pod], type) #ssgid
    #            print "Valid template dict", vapp_template_dict
                if len(vapp_template_dict) != 0:
                    valid_enm_vapp_template_dict.update(vapp_template_dict)
            '''
            current_sprint = sprint_list[0]
            previous_sprint = sprint_list[1]
            ssgid_template_count = 1
            full_template_count = 1
            for sprint in sprint_list:
                if sprint == current_sprint:
                    if type == 'SSGID':
                        count = 3
                    elif type == 'FULL':
                         if pod == "G" or pod == "E":
			    count = 1
			 else:
			    count = 2
                    vapp_template_dict = get_valid_templates(sprint, pods[pod], type, count)
                    if len(vapp_template_dict) != 0:
                        valid_enm_vapp_template_dict.update(vapp_template_dict)
			if pod == "G" or pod == "E":
			    full_template_count = 0
                    else:
                        if type == 'SSGID':
                            ssgid_template_count = 3
                        elif type == 'FULL': 
			     if pod == "G" or pod == "E":
				full_template_count = 1
			     else:
				full_template_count = 2
                elif sprint == previous_sprint:
                    if type == 'SSGID':
                        count = ssgid_template_count
                    elif type == 'FULL':
                        count = full_template_count
                    vapp_template_dict = get_valid_templates(sprint, pods[pod], type, count)
                    if len(vapp_template_dict) != 0:
                        valid_enm_vapp_template_dict.update(vapp_template_dict)
                else:
                    if (pod == "G" or pod == "E" and type == 'FULL'):
			vapp_template_dict = get_valid_templates(sprint, pods[pod], type, count=0)
		    else:
			vapp_template_dict = get_valid_templates(sprint, pods[pod], type, count=1)
                    if len(vapp_template_dict) != 0:
                        valid_enm_vapp_template_dict.update(vapp_template_dict)



            print "Valid "+type+" templates"#, ssgid_valid_enm_vapp_template_dict
            for key in sorted(valid_enm_vapp_template_dict.keys(), reverse=1):
                    print  str(key)+" : "+str(valid_enm_vapp_template_dict[key])

            for key in all_enm_vapp_template_dict.keys():
                if key not in valid_enm_vapp_template_dict.keys():
                    enm_vapp_template_delete_dict[key]=all_enm_vapp_template_dict[key]


            if len(enm_vapp_template_delete_dict) == 0:
                print "No templates to be deleted"
            else:
                print "\n"+type+" Templates to be deleted"
                for key in sorted(enm_vapp_template_delete_dict.keys(),reverse=1):
                    print  str(key)+" : "+str(enm_vapp_template_delete_dict[key])
            print "\n"


            for temp_name,temp_id in enm_vapp_template_delete_dict.items():
                command_to_delete_template = str(CURL) + ' -u administrator:admin01 --insecure ' + pods[pod] + \
                str(spp_api_to_delete_template) + str(temp_id) + '/.xml'
#                print "Command: ", command_to_delete_template
                print "Deleting Template: ", temp_name
                template_del = subprocess.Popen(command_to_delete_template.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                (stdout,stderr) = template_del.communicate()
                print "Template "+temp_name+" deleted"
            print "=============================\n\n\n\n\n"

if __name__ == '__main__':
        main(sys.argv[1:])
                                                                                                                                                        
