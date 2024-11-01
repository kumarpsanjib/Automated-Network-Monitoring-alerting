from netmiko import ConnectHandler
from twilio.rest import Client
import requests
import subprocess

# Twilio Configurations
account_sid='ACcf882611956338d1ea2173c8342dc4ed'
auth_token='bb9a295828738361811bcfa936ff8577'
twilio_client=Client(account_sid,auth_token)
twilio_phn_no=+18583466371

# Mailgun Configurations
mailgun_api_key = '80641f5a0ccd267839ebf8dd9ae849b4-784975b6-84a2d8f1'
mailgun_domain = 'sandboxb84a64d6bfff41b78bf7d335e9ffac66.mailgun.org'

# Opens the files for credentials and device info
with open("config_5routers_credentials") as f:
    creds=f.read().splitlines()
with open("config_5routers_info") as f:
    conf=f.read().splitlines()

# Creating device list
device_list=list()
num_cred=len(creds)
for i, device in enumerate(conf):
    if(i*3)+2>=num_cred:
        print(f"Credential is not enough for the : {device}")
        break
    username=creds[i*3]
    password=creds[i*3+1]
    secret=creds[i*3+2]
    cisco_device={
        'device_type':"cisco_ios",
        'host':device,
        'username':username,
        'password':password,
        'port':22,
        'secret':secret,
        'verbose':True
    }
    device_list.append(cisco_device)

# Message function for Twilio
def send_msg(message):

    try:
        message = twilio_client.messages.create(
            body=message,
            from_=twilio_phn_no,
            to='+918249252818'
        )
        print(f"Twilio message sent.")
    except Exception as e:
        print(f"Failed to send Twilio message: {e}")

# Email function for Mailgun
def send_email(subject,message_body):
    try:
       response= requests.post(
           f"https://api.mailgun.net/v3/sandboxb84a64d6bfff41b78bf7d335e9ffac66.mailgun.org/messages",
           auth=("api",'80641f5a0ccd267839ebf8dd9ae849b4-784975b6-84a2d8f1'),
           data={
               "from" : f"Mailgun Sandbox <postmaster@sandboxb84a64d6bfff41b78bf7d335e9ffac66.mailgun.org>",
               "to" : "kumarpriti07@outlook.com",
               "subject" : subject,
               "text" : message_body

           })
       print("Email sent.")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Configuring OSPF on device
def configure_ospf(connect):
    print(f"Configuring OSPF on {connect.host}...")
    current_prompt = connect.find_prompt()
    print(f"Current prompt: {current_prompt}")

    if '>' in current_prompt:  # Ensure we're in user EXEC mode
        connect.enable()  # Enter privileged EXEC mode

    try:
        connect.config_mode()  # Enter configuration mode
        commands = ['router ospf 1', 'network 0.0.0.0 0.0.0.0 area 0', 'exit']
        connect.send_config_set(commands)
        print(f"OSPF configured on {connect.host}.")
    except Exception as e:
        print(f"Error entering config mode on {connect.host}: {e}")

# Used to check reachability of the device
def is_device_reachable(ip_address):
    """Ping the device to check if it's reachable."""
    response = subprocess.run(['ping', ip_address], stdout=subprocess.PIPE)
    return response.returncode == 0

# Monitor device function
def monitor_device(device):
    ip_address = device['host']
    if not is_device_reachable(ip_address):
        print(f"{ip_address} IS UNREACHABLE. SENDING AN ALERT TO YOUR PHONE NUMBER.....")
        send_msg(f"ALERT: Device {ip_address} is unreachable.")
        print(f"Message Send successfully to your phone number")
        print(f"{ip_address} IS UNREACHABLE. SENDING AN ALERT TO YOUR EMAIL-ID.....")
        send_email(f"ALERT: Device {ip_address} is unreachable", f"Failed to connect to {ip_address}.")
        print(f"Message Send successfully to your email-id")
        print("*"*50)
        return

    try:
        print(f"CONNECTING TO {device['host']}......")
        print("-"*50)
        connect = ConnectHandler(**device)
        if '>' in connect.find_prompt():
            connect.enable()
        interface_status=connect.send_command("sh ip int brief")
        print(f"Monitoring {device['host']}.")

        interfaces_to_monitor = ['Ethernet0/0', 'Ethernet0/1', 'Ethernet0/2']

        alert_triggered=False

        for interface in interfaces_to_monitor:
            if interface in interface_status:
                for line in interface_status.splitlines():
                    if interface in line:
                        status_columns = line.split()
                        interface_state = status_columns[4]  # Assuming the 5th column has the state

                        if interface_state == "administratively down":
                            print(f"{interface} is administratively down on {device['host']}.")
                            send_msg(f"Notice: {interface} administratively down on {device['host']}.")
                            send_email(f"Notice: {interface} Administratively down", interface_status)
                        elif interface_state == "down":
                            print(f"{interface} is down on {device['host']}.")
                            send_msg(f"Alert: {interface} down on {device['host']}.")
                            send_email(f"Alert: {interface} Down", interface_status)
                            alert_triggered = True
                            print(f"Attempting to bring {interface} back up on {device['host']}...")

                        else:
                            print(f"{interface} is up on {device['host']}.")
        if not alert_triggered:
            print(f"No interface issues detected on {device['host']}.")

        conf_backup=connect.send_command('show running-config')
        with open(f"Backup {device['host']}.txt","w") as bfile:
            bfile.write(conf_backup)
        print(f"Backup Completed for {device['host']}")
        print(f"Backup stored in: <Backup {device['host']}.txt>")
    except Exception as e:
        print(f"Failed to connect to {device['host']}: {e}")
    finally:
        if 'connect' in locals():
            print(f"Closing connection of {device['host']}......")
            connect.disconnect()
            print("*"* 50)

for device in device_list:
    monitor_device(device)