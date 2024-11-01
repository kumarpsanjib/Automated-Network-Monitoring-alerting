# Automated Network Device Monitoring, Alerting and Configuration of Backup System
This project is designed to provide an efficient, automated solution for **real-time network monitoring, alerting, and configuration backup**, using **Python** and it's **networking libraries**.

### **Project Overview**

**Monitors network devices** in a simulated **EVE-NG** environment, using **SSH connections** to retrieve interface status and configurations.

**Generates real-time alerts** (SMS and email) via **Twilio** and **Mailgun** for down interfaces, enhancing response time for troubleshooting.

**Automates configuration backups** for each monitored device, ensuring recent configurations are always available for restoration.

### **Key Features**

**Device Status Monitoring:** Tracks device and interface states across multiple network devices.

**Alerting System:** Sends SMS and email notifications on device/interface failures to a designated contact for proactive action.

**Configuration Backup:** Automatically backs up the latest configuration files to ensure network consistency.

**Dynamic File Handling:** Credentials and IP details for routers are securely sourced from external files, improving data management.

### **Technologies Used**

**Libraries:** **Netmiko** (SSH connections), **Requests** (API handling), **Twilio** (SMS alerts), **Mailgun** (email alerts)

**Environment:** **EVE-NG** for network simulation, **PyCharm** for development 
