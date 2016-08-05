## Description

This API is built on Django to make scaling using HAProxy LB much easier.

The API is deployed on AWS and uses the size of the EC2 instance to determine the weight that should be assigned on HAProxy.
The formula followed to determine the weight of the instance is : round(memory + vcpu * ecu)

EX: If the size of the EC2 instance is M4.large the weight would be round(8 + 6.5 * 2 ) = 21

Note: The API is designed to be used internally on local subnets.

## Features

- Add New Server to Backend
- Remove Server from Backend
- Reload HAProxy

## Response

- 200 (For all successful requests)
- Still under developement

## Getting Started

###Install
```
cd /home
git clone https://github.com/Vinelab/haproxy-config-manager
pip install -r requirements.txt
cd /home/haproxy-config-manager
```
Make sure port 8001 inbound is open on local subnet

###Run
```
sudo uwsgi --http :8001 --wsgi-file ProxyAPI/wsgi.py --enable-threads --daemonize=/home/haproxy-config-manager/uwsgi-api.log
```

###API Calls
####Curl
#####Add Server to Backend
```
http://HAPROXYAPI_IP:8001/api/add/?instance_id=INSTANCE_ID&backend=BACKEND_NAME&port_numb=PORT_NUMBER&private_ip=INSTANCE_IP&type=INSTANCE_TYPE
```
#####Remove Server from Backend
```
http://HAPROXYAPI_IP:8001/api/remove/?instance_id=INSTANCE_ID&port_numb=PORT_NUMBER&private_ip=INSTANCE_IP&type=INSTANCE_TYPE
```
#####Reload HAProxy Config
```
http://HAPROXYAPI_IP:8001/api/reload
```
###AWS Opsworks Recipes
####Recipe to Deploy and Run HAProxy API
```
script 'clone_code' do
    interpreter 'bash'
    cwd "/home"
    code <<-EOH
    git clone https://github.com/Vinelab/haproxy-config-manager
EOH

end

script 'install_requirements' do
    interpreter 'bash'
    cwd "/home/haproxy-config-manager"
    code <<-EOH
    pip install -r requirements.txt
EOH

end

script 'launch_deamon' do
    interpreter 'bash'
    cwd "/home/haproxy-config-manager"
    code <<-EOH
    sudo uwsgi --http :8001 --wsgi-file ProxyAPI/wsgi.py --enable-threads --daemonize=/home/haproxy-config-manager/uwsgi-api.log
EOH

end
```
####Attributes default.rb
```
#General Attributes
default[:instance] = {}
default[:instance]['instance_id'] = node['opsworks']['instance']['aws_instance_id']
default[:instance]['private_ip'] = node['opsworks']['instance']['private_ip']
#haproxy api specific attributes
default[:haproxyapi] = {}
default[:haproxyapi]['private_ip'] = node['haproxy_ip']
default[:haproxyapi]['backend'] = node['backend']
#haproxy opsworks related attributes
default[:instance]['id'] = node["opsworks"]["instance"]["id"]
default[:instance]['instance_type'] = node["opsworks"]["instance"]["instance_type"]
default[:instance]['stack_id'] = node["opsworks"]["stack"]["id"]
```
####Custom JSONs
- The HAProxy Private IP should be in the stack custom JSON.
```
{
"haproxy_ip":"xxx.xxx.xxx.xxx"
}
```
- The Backend that the instance should be added to needs to be present in the layer's custom JSON.
```
{
"backend":"najem"
}
```
####Recipe to Add Server
```
#API Request to add instance to Load Balancer

http_request '' do
    
    url "http://#{node[:haproxyapi]['private_ip']}:8001/api/add/?instance_id=#{node[:instance]['instance_id']}&backend=#{node[:haproxyapi]['backend']}&port_numb=80&private_ip=#{node[:instance]['private_ip']}&type=#{node["opsworks"]["instance"]["instance_type"]}"

end
```
####Recipe to Remove Server
```
#API Request to remove instance from Load Balancer

http_request '' do
    
    url "http://#{node[:haproxyapi]['private_ip']}:8001/api/remove/?instance_id=#{node[:instance]['instance_id']}&port_numb=80&private_ip=#{node[:instance]['private_ip']}&type=#{node["opsworks"]["instance"]["instance_type"]}"

end
```
####Recipe to Reload config
```
#API replace request

http_request '' do
    
    url "http://#{node[:haproxyapi]['private_ip']}:8001/api/reload"

end
```

