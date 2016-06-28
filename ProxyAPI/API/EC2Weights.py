import json
import os
import urllib2
from datetime import datetime


class EC2Weights:

    def __init__(self, instance_type):

        self.instance_type = instance_type
        self.instances_info_path = 'instances.json'
        self.instances_info_url = 'http://www.ec2instances.info/instances.json'
        self.file_max_age = 7

        if os.path.isfile(self.instances_info_path):
            # If instance info is >= to file_max_age re-fetch the data
            if self.latest_edit() >= self.file_max_age:
                self.fetch_data()
            with open(self.instances_info_path) as instances:
                self.data = json.load(instances)
        else:
            self.fetch_data()

    # Calculate weight
    def get_weight(self):

        instance_index = self.get_instance_index()

        memory = self.data[instance_index]['memory']
        vcpu = self.data[instance_index]['vCPU']

        # Check if instance is burstable
        if self.data[instance_index]['ECU'] == 'variable':
            ecu = 1
        else:
            ecu = self.data[instance_index]['ECU']

        return memory + vcpu * ecu

    # Find index in the list of dictionaries
    def get_instance_index(self):
        for index in range(len(self.data)):
            if self.data[index]['instance_type'] == self.instance_type:
                return index

    # Check latest edit
    def latest_edit(self):
        file_modified_date = datetime.fromtimestamp(os.path.getmtime(self.instances_info_path))
        return abs((datetime.today() - file_modified_date).days)

    # Fetch data from url
    def fetch_data(self):
        try:
            instances_json = urllib2.urlopen(self.instances_info_url)
            self.data = json.loads(instances_json.read())
            with open(self.instances_info_path, 'w') as outfile:
                json.dump(self.data, outfile)
        except:
            print "cad"
            with open(self.instances_info_path) as instances:
                self.data = json.load(instances)


weight = EC2Weights('t2.nano')
print weight.get_weight()
