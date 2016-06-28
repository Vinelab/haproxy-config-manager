import os
import shutil
from datetime import datetime
import slackweb
import EC2Weights


class HAProxyManager:
    def __init__(self):
        self.slack_incoming_webhook = "YOUR_SLACK_WEBHOOK_HERE"
        self.slack = slackweb.Slack(url=self.slack_incoming_webhook)
        self.haproxy_config = "/etc/haproxy/haproxy.cfg"
        self.haproxy_config_temp = "/etc/haproxy/haproxy_temp.cfg"
        self.backup_path = "/etc/haproxy/backup/"
        self.logs = "/etc/haproxy/log.txt"
        self.interval = "5000"
        self.fastinterval = "1000"
        self.fall = "1"
        self.weight = "1"

    # Replace Temp config to actual config after editing
    def replace_config(self):
        self.log_writer("Replacing Config")
        shutil.copy2(self.haproxy_config_temp, self.haproxy_config)

    # Replace clone config
    # Used as an API call to reload HAProxy with a working config file
    def replace_haconfig(self):
        shutil.copy2(self.haproxy_config_temp, self.haproxy_config)
        self.reload_haproxy()
        if self.slack_incoming_webhook.__contains__("http"):
            slackmessage = "HA Proxy Reloaded and Replaced Config"
            self.slack.notify(text=slackmessage)

    # Append log to HAProxy directory log.txt
    def log_writer(self, message):
        log = open(self.logs, 'a')
        log.write(datetime.now().time().isoformat() + ' : ' + message + '\n')
        log.close()

    # Backup old configuration
    def backup_config(self):
        self.log_writer("Backing up Config")

        # Specify backup directory
        backup_dir = os.path.dirname(self.backup_path)

        # Check if Backup dir exists, if not it creates the directory
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)

        # If an older backup version exists it increments its name before overwriting it
        if os.path.isfile(self.backup_path + 'haproxy_old_1.cfg'):
            shutil.copy2(self.backup_path + 'haproxy_old_1.cfg', self.backup_path + 'haproxy_old_2.cfg')

        # Overwrite backup file
        shutil.copy2(self.haproxy_config, self.backup_path + 'haproxy_old_1.cfg')

    # Boolean method to check if server exists to prevent duplicate servers
    def server_exists(self, server_config):
        haproxy_config_file = open(self.haproxy_config, 'r')

        if haproxy_config_file.read().find(server_config) == -1:
            return False
        else:
            return True

        haproxy_config_file.close()

    # Graceful Reload for HAProxy on the OS level
    def reload_haproxy(self):
        self.log_writer("reloading haproxy")

        command = "haproxy -D -f /etc/haproxy/haproxy.cfg -p /var/run/haproxy.pid -sf $(cat /var/run/haproxy.pid)"
        os.system(command)

    # Generate new line for a backend server
    def get_new_server_config(self, server_name, server_ip, server_port, instance_type):

        # Check if instance type is available
        if len(instance_type) > 0:
            weight = self.calculate_weight(instance_type)
        else:
            # Set default weight
            weight = self.weight

        return "    server %s %s:%s check inter %s fastinter %s fall %s weight %s cookie %s\n" % (
            server_name, server_ip, server_port, self.interval, self.fastinterval, self.fall,
            weight, server_name)

    # Method to send a slack message
    def notify(self, slackmessage):

        # Send slack message if valid web hook available
        if self.slack_incoming_webhook.__contains__("http"):
            self.slack.notify(text=slackmessage)

    # Method called from the API
    # Method that manages the adding server process
    def add_server(self, backend_name, server_name, server_ip, server_port, instance_type):

        # Backup Config
        self.backup_config()

        # Generate line that should be added in the file
        new_server_config = self.get_new_server_config(server_name, server_ip, server_port, instance_type)

        # Check if server already exists
        if not self.server_exists(new_server_config):
            haproxy_config_file = open(self.haproxy_config, 'r')
            haproxy_config_temp = open(self.haproxy_config_temp, 'w')

            for line in haproxy_config_file.readlines():

                haproxy_config_temp.write(line)

                if line == "backend %s\n" % backend_name:
                    # Append backend line to the backend specified
                    haproxy_config_temp.write(new_server_config)

            haproxy_config_file.close()
            haproxy_config_temp.close()

            # Export log
            self.log_writer('NEW SERVER ' + new_server_config)

            # Send slack message
            slackmessage = "New Server %s %s added to %s" % (server_name, server_ip, backend_name)
            self.notify(slackmessage)

            # Replace config and reload HAProxy
            self.replace_config()
            self.reload_haproxy()

        else:
            self.log_writer("Duplicate Server found %s | %s" % (server_name, server_ip))

    # Method called from the API
    # Method that manages the remove server process
    def remove_server(self, server_name, server_ip, server_port):

        # Backup Config
        self.backup_config()

        # Generate line that should be added in the file
        new_server_config = self.get_new_server_config(server_name, server_ip, server_port)

        if self.server_exists(new_server_config):
            haproxy_config_file = open(self.haproxy_config, 'r')
            new_haproxy_config = open(self.haproxy_config_temp, 'w')

            for line in haproxy_config_file.readlines():

                # Remove backend server from config file
                if not line == new_server_config:
                    new_haproxy_config.write(line)

            haproxy_config_file.close()
            new_haproxy_config.close()

            # Export log
            self.log_writer('REMOVED SERVER ' + new_server_config)

            # Send slack message
            slackmessage = "Server %s %s was removed" % (server_name, server_ip)
            self.notify(slackmessage)

            # Replace config and reload HAProxy
            self.replace_config()
            self.reload_haproxy()

        else:
            self.log_writer("Server not found %s | %s" % (server_name, server_ip))

    # Calculate weight based on instance type
    def calculate_weight(self, instance_type):

        print instance_type
        weight = EC2Weights.EC2Weights(instance_type)
        return weight.get_weight()

