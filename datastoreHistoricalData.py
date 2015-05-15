import os
import sys
import fileinput
import requests

from requests.auth import HTTPBasicAuth
from xml.etree.ElementTree import ElementTree, Element, SubElement, tostring, Comment
from xml.etree.ElementTree import ParseError
import xml.dom.minidom as minidom

hostsys_resource = []
virtualm_resource = []
datacenter_resource = []
cluster_resource = []
other_resource = []

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    roughString = tostring(elem, 'utf-8')
    reparsed = minidom.parseString(roughString)
    return reparsed.toprettyxml(indent="\t")

def get_resources():
    # Get list of resources

    cloud = {"name": "angola"}
    resourceUrl = 'https://10.4.43.64/suite-api/api/resources'

    try:
        response = requests.get(resourceUrl, params=cloud, auth=HTTPBasicAuth('admin', 'Apple4u2$'), verify=False)

        with open("data.xml","w") as xFile:
            xFile.write(response.text)

    except:
        print "Unexpected Error :", sys.exc_info()[0]

    # Replace unexpected ops text from tag name
    for line in fileinput.input('data.xml', inplace=True):
        print line.replace('ops:', '')


    # List the datastores in resources
    tree = ElementTree()
    try:
        tree.parse(os.getcwd() + os.path.sep + "data.xml")
    except IndexError as exc:
        print "Error : Input File is not mentioned, Please specify the Input File."
        sys.exit(1)
    except ParseError as exc:
        print "Error : Not a valid Input File -", exc
        sys.exit(1)
    except:
        print sys.exc_info()[0]
        sys.exit(1)

    # Populated the necessary details for all the available resources
    availResources = []
    root = tree.getroot()
    for xResource in root.findall('resource'):
        resourceDescription = {}
        resourceDescription['id'] = xResource.attrib['identifier']
        resourceDescription['name'] = xResource.find('resourceKey/name').text
        resourceDescription['kind'] = xResource.find('resourceKey/resourceKindKey').text
        availResources.append(resourceDescription)

    return availResources

def get_resource_stat_keys(resourceId):
    # Get the statkeys for a specific resource
    resourceStatKeysUrl = 'https://10.4.43.64/suite-api/api/resources/statkeys'
    params = {}
    params['resourceId'] = resourceId
    try:
        response = requests.get(resourceStatKeysUrl, auth=HTTPBasicAuth('admin', 'Apple4u2$'), verify=False, params=params)

        with open("data.xml","w") as xFile:
            xFile.write(response.text)

    except:
        print "Unexpected Error :", sys.exc_info()[0]

    # Replace unexpected ops text from tag name
    import fileinput
    for line in fileinput.input('data.xml', inplace=True):
        print line.replace('ops:', '')

    tree = ElementTree()
    try:
        tree.parse(os.getcwd() + os.path.sep + "data.xml")
    except IndexError as exc:
        print "Error : Input File is not mentioned, Please specify the Input File."
        sys.exit(1)
    except ParseError as exc:
        print "Error : Not a valid Input File -", exc
        sys.exit(1)
    except:
        print sys.exc_info()[0]
        sys.exit(1)

    availStatKeys = []
    root = tree.getroot()
    for xKey in root.findall('stat-key/key'):
        availStatKeys.append(xKey.text)
    return availStatKeys

'''
def get_resource_statkey_data(resourceId, statKey, dataFile):
    # Get the data for perticular stat-key
    resourceStatDataUrl = 'https://10.4.43.64/suite-api/api/resources/stats/latest'
    params = {}
    params['resourceId'] = resourceId
    params['statKey'] = statKey
    print "Parameter :",params
    try:
        response = requests.get(resourceStatDataUrl, auth=HTTPBasicAuth('admin', 'Apple4u2$'), verify=False, params=params)

        with open("data.xml","w") as xFile:
            xFile.write(response.text)

    except:
        print "Unexpected Error :", sys.exc_info()[0]

    # Replace unexpected ops text from tag name
    import fileinput
    for line in fileinput.input('data.xml', inplace=True):
        print line.replace('ops:', '')

    tree = ElementTree()
    try:
        tree.parse(os.getcwd() + os.path.sep + "data.xml")
    except IndexError as exc:
        print "Error : Input File is not mentioned, Please specify the Input File."
        sys.exit(1)
    except ParseError as exc:
        print "Error : Not a valid Input File -", exc
        sys.exit(1)
    except:
        print sys.exc_info()[0]
        sys.exit(1)

    root = tree.getroot()

    for xStats in root.findall('stats-of-resource/stat-list/stat/data'):
        dataFile.write('Resource Id:' + resourceId)
        dataFile.write('\n')
        dataFile.write('---------------------------------------------')
        dataFile.write('\n')
        dataFile.write('Stat Data=' + xStats.text)
        dataFile.write('\n\n')
'''

def get_resource_data(resourceId, dataFile):
    """Get the data for particular resource"""

    resourceStatDataUrl = 'https://10.4.43.64/suite-api/api/resources/stats/latest'
    params = {}
    params['resourceId'] = resourceId
    print "Parameter :",params
    try:
        response = requests.get(resourceStatDataUrl, auth=HTTPBasicAuth('admin', 'Apple4u2$'), verify=False, params=params)

        with open("data.xml","w") as xFile:
            xFile.write(response.text)

    except:
        print "Unexpected Error :", sys.exc_info()[0]

    # Replace unexpected ops text from tag name
    import fileinput
    for line in fileinput.input('data.xml', inplace=True):
        print line.replace('ops:', '')

    tree = ElementTree()
    try:
        tree.parse(os.getcwd() + os.path.sep + "data.xml")
    except IndexError as exc:
        print "Error : Input File is not mentioned, Please specify the Input File."
        sys.exit(1)
    except ParseError as exc:
        print "Error : Not a valid Input File -", exc
        sys.exit(1)
    except:
        print sys.exc_info()[0]
        sys.exit(1)


    root = tree.getroot()

    dataFile.write('Resource Id:' + resourceId)
    dataFile.write('\n')
    dataFile.write('---------------------------------------------')
    dataFile.write('\n')

    for xStats in root.findall('stats-of-resource/stat-list/stat'):
        #Write resource data to file
        dataFile.write('Stat-Key: ')
        dataFile.write(xStats.find('statKey/key').text)
        dataFile.write('\n')

        dataFile.write('Timestamp: ')
        dataFile.write(xStats.find('timestamps').text)
        dataFile.write('\n')

        dataFile.write('Data: ')
        dataFile.write(xStats.find('data').text)
        dataFile.write('\n')

        dataFile.write('\n\n')

def filter_resources(resourcelist):
    """ This method filters the resources based on their kind"""

    for i in range(len(resourcelist)):
        if resourcelist[i]['kind'] == 'HostSystem':
            hostsys_resource.append(resourcelist[i])
        elif resourcelist[i]['kind'] == 'VirtualMachine':
            virtualm_resource.append(resourcelist[i])
        elif resourcelist[i]['kind'] == 'Datacenter':
            datacenter_resource.append(resourcelist[i])
        elif resourcelist[i]['kind'] =='ClusterComputeResource':
            cluster_resource.append(resourcelist[i])
        else:
            other_resource.append(resourcelist[i])

    print 'Filtered Lists of different resources are:' + '\n'
    print 'hostsystem list = ', hostsys_resource

    print 'virtualmachine list = ', virtualm_resource

    print 'datacenter resource list = ', datacenter_resource

    print 'clustercompute resource list = ', cluster_resource

    print 'other resource list = ', other_resource

def prepare_final_data(resourcelist, fname, data_dir):
    """ Prepare stat data files based on resource-type """

    # Create sub-directory based on resource type
    sub_dir = data_dir + os.path.sep + fname
    if not(os.path.exists(sub_dir)):
        os.mkdir(sub_dir)

    for resources in resourcelist:
        file_name = sub_dir + os.path.sep + fname + resources['id']

        with open(file_name, 'w') as f_name:
            get_resource_data(resources['id'], f_name)

def main():
    availResources = get_resources()
    print "Available Resources - ", availResources
    print '+'+'-'*70+'+'

    filter_resources(availResources)

    '''
    resourceStatKeys = get_resource_stat_keys(availResources[0]['id'])
    print "Available Stat Keys - ", resourceStatKeys

    resource_stat = open('datReport.txt', 'w')

    for i in range(len(availResources)):
        get_resource_data(availResources[i]['id')

    resource_stat.close()
    '''

    data_dir = os.getcwd() + os.path.sep + 'ResourceData'

    # Create directory to store data
    if not(os.path.exists(data_dir)):
        os.mkdir(data_dir)

    # Get the final data from each type of resource

    # Host_System resource data
    prepare_final_data(hostsys_resource, 'HostSystem', data_dir)

    # Virtual Machine resource data
    prepare_final_data(virtualm_resource, 'VirtualMachine', data_dir)

    # DataCenter resource data
    prepare_final_data(datacenter_resource, 'Datacenter', data_dir)

    # ClusterComputeResource data
    prepare_final_data(cluster_resource, 'ClusterComputeResource', data_dir)

    # Other Resources data
    prepare_final_data(other_resource, 'OtherResource', data_dir)

if __name__ == "__main__":
    main()