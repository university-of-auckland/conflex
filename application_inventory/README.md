# Application Inventory Tool

The script in this folder basically takes information from the main Connex application and puts it into the previously
used database tables. This allows the application to be backwards compatible whilst enabling new information to be 
retrieved from the wiki by simply changing a couple of lines in a configuration file.

*Note: This tool does not delete any information from the current tables, it will only update current pages/insert new
ones.*

## Configuration
The configuration file that this tool uses must be named `app_config.yaml`.

### Example Configuration
```
mysql:
  host: 127.0.0.1
  port: 3306
  database: connex
  username:
  password:
  wiki_table_prefix: wiki

logging:
  level: DEBUG

application:
  labels:
    info:
      - Account Manager
      - Common Names
      - External Users Allowed
      - Implementation Year
      - Last Upgrade Year
      - Life Cycle Phase
      - Platform
      - Software Licensing Model
      - Tech Contact
      - Type
      - Vendor
      - Version
      - CAUDIT Capability L0
      - CAUDIT Capability L1
    stakeholder:
      - Business Owner
      - Organisation Owner
      - Service Manager
      - Service Owner
      - Subject Matter Experts
    nfr:
      - Data Sensitivity
      - Hosting Tier
      - Hours of Support
      - Hours of Use
      - Maintenance Windows
      - Patching Cycle
      - RPO Current
      - RPO Required
      - RTO Current
      - RTO Required
      - Service Criticality
      - TIME Fitness
      - TIME Value
      - TIME Cost
    support:
      - 1st Level Support
      - 2nd Level Support
      - 3rd Level Support
      - Development
      - 3rd Level Support
      - Operational
      - Application Data
      - Platform
      - Database
      - Load Balancer
      - Operating System
      - OS Patching
      - Hypervisor
      - Guest Servers
      - Storage- Network
    arch:
      - User Interface Type
      - Mobile Support
      - UI Technology
      - Authentication
      - Authorisation
      - Hosting
      - Resilience
      - API
      - Middleware Technology
      - Web Server
      - App Server
      - Operating System
      - Database
      - Monitoring
      - Alerting Destination
      - Backup
      - f5 SSL Profile(s)
    app_tiny_url:
      - webui
      - tinyui
    app_description:
      - Overview
      - Roadmap
```