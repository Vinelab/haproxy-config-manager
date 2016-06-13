import os
import shutil
from datetime import datetime
import slackweb

class HAProxyManager:

    def __init__(self):
        self.slack_incoming_webhook = "WEB_HOOK_HERE"
        self.slack = slackweb.Slack(url=self.slack_incoming_webhook)
        self.haproxy_config_path = "/etc/haproxy/haproxy.cfg"
        self.haproxy_config_temp_path = "/etc/haproxy/haproxy_temp.cfg"
        self.backup_path = "/etc/haproxy/backup/"
        self.logs = "/etc/haproxy/log.txt"
        self.interval = "5000"
        self.fastinterval = "1000"
        self.fall = "1"
        self.weight = "1"

    def replace_config(self):

        self.log_writer("Replacing Config")
        shutil.move(self.haproxy_config_temp_path, self.haproxy_config_path)

    def log_writer(self, message):

        log = open('/etc/haproxy/log.txt', 'a')
        log.write(datetime.now().time().isoformat()+' : ' + message+'\n')
        log.close()

    def backup_config(self):

        self.log_writer("Backing up Config")

        backup_dir = os.path.dirname(self.backup_path)

        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)

        if os.path.isfile(self.backup_path + 'haproxy_old_1.cfg'):
            shutil.copy2(self.backup_path + 'haproxy_old_1.cfg', self.backup_path + 'haproxy_old_2.cfg')

        shutil.copy2(self.haproxy_config_path, self.backup_path + 'haproxy_old_1.cfg')

    def server_exists(self, server_config):

        haproxy_config_file = open(self.haproxy_config_path, 'r')

        if haproxy_config_file.read().find(server_config) == -1:
            return False
        else:
            return True

        haproxy_config_file.close()

    def reload_haproxy(self):

        self.log_writer("reloading haproxy")

        command = "haproxy -D -f /etc/haproxy/haproxy.cfg -p /var/run/haproxy.pid -sf $(cat /var/run/haproxy.pid)"
        os.system(command)

    def get_new_server_config(self, server_name, server_ip, server_port):

        return "    server %s %s:%s check inter %s fastinter %s fall %s weight %s cookie %s\n" % (
            server_name, server_ip, server_port, self.interval, self.fastinterval, self.fall,
            self.weight, server_name)

    def add_server(self, backend_name, server_name, server_ip, server_port):

        self.backup_config()

        new_server_config = self.get_new_server_config(server_name, server_ip, server_port)

        if not self.server_exists(new_server_config):
            haproxy_config_file = open(self.haproxy_config_path, 'r')
            new_haproxy_config = open(self.haproxy_config_temp_path, 'w')

            for line in haproxy_config_file.readlines():

                new_haproxy_config.write(line)

                if line == "backend %s\n" % backend_name:
                    new_haproxy_config.write(new_server_config)

            haproxy_config_file.close()
            new_haproxy_config.close()

            self.log_writer('NEW SERVER ' + new_server_config)

            if self.slack_incoming_webhook.__contains__("http"):
                slackmessage = "New Server %s %s added to %s"%(backend_name, server_name, server_ip)
                self.slack.notify(text=slackmessage)

            self.replace_config()
            self.reload_haproxy()

        else:
            self.log_writer("Duplicate Server found %s | %s"%(server_name, server_ip))

    def remove_server(self, server_name, server_ip, server_port):

        self.backup_config()

        new_server_config = self.get_new_server_config(server_name, server_ip, server_port)

        if self.server_exists(new_server_config):
            haproxy_config_file = open(self.haproxy_config_path, 'r')
            new_haproxy_config = open(self.haproxy_config_temp_path, 'w')

            for line in haproxy_config_file.readlines():

                if not line == new_server_config:
                    new_haproxy_config.write(line)

            haproxy_config_file.close()
            new_haproxy_config.close()

            self.log_writer('REMOVED SERVER ' + new_server_config)

            if self.slack_incoming_webhook.__contains__("http"):
                slackmessage = "Server %s %s was removed" % (server_name, server_ip)
                self.slack.notify(text=slackmessage)

            self.replace_config()
            self.reload_haproxy()

        else:
            self.log_writer("Server not found %s | %s" % (server_name, server_ip))
