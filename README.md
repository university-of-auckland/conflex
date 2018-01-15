# Wiki To Capsule Integration Application

This application is designed to replace the current Wiki-to-Capsule Integration application that is written in 
Java/Groovy and run through Scriptella.

For more information about the Application, please see the following 
[wiki page](https://wiki.auckland.ac.nz/display/APPLCTN/Capsule+Future+State+Application+Design)

## Running The Application
This application is written using python v3.6. It is advisable but not necessary to run the application 
using virtualenv. Please install the required libraries through pip using: `pip install -r requirements.txt`

To run the application simply pass the containing folder to the python interpreter and the `__main__.py` will be 
invoked. i.e. `python /path/to/capsule`.

## Making Documentation
The application supports documentation through Sphinx. To generate the Documentation run `make html`. Currently the
only way to do this is through the `Makefile`, the `make.bat` script has not been correctly configured.

## Configuration

### Example Configuration

```
confluence:
  host: https://wiki.auckland.ac.nz
  port: 443
  username:
  password:

mysql:
  host: 127.0.0.1
  port: 3306
  database: capsule
  username: 
  password: 

wiki:
  spaces:
    - APPLCTN:
        pages:
          labels:
            - application:
                panels:
                  - Overview
                  - Roadmap
                  - Infrastructure
                page_properties:
                  - inv_item_info
                  - itil_stakeholders
                  - nfr
                pages:
                  labels:
                    - support_model:
                        page_properties:
                          - support_model
                          - support_tiers
                    - inv_architecture_overview:
                        page_properties:
                          - inv_architecture_info
    - REFARCH:
        pages:
          titles:
            - Information Architecture:
                pages:
                  titles:
                    - Information Entities
            - Technology Architecture:
                pages:
                  labels:
                    - service-area-metadata:
                        headings:
                          - Definition
                          - Principles
                          - Standards
                          - Guidelines
                          - Security
                          - Monitoring
                          - Resilience
                          - Recovery
                          - Future
                        pages:
                          labels:
                            - domain-metadata:
                                headings:
                                  - Overview
                                  # Repeated #
                                  - Principles
                                  - Standards
                                  - Guidelines
                                  - Security
                                  - Monitoring
                                  - Resilience
                                  - Recovery
                                  - Future
                                  # Repeated #
                                pages:
                                  labels:
                                    - brick-metadata:
                                        pages:
                                          labels:
                                            - element-metadata
```
### Wiki Configuration

The example configuration above contains a configuration definition for `wiki`. This configures the capsule application
so that it knows where and what information the application is to retrieve. The  `wiki` configuration adheres to the
following design guideline.

```
wiki:
  spaces:
    - [LIST OF SPACE NAMES]:
        pages:
          [PAGE NAVIGATION]:
            [PAGE INFORMATION RETRIEVAL TYPE]
              - [LIST OF INFORMATION TO RETRIEVE]
```

#### Wiki Descriptors

| Keyword | Description |
| ------- | ----------- |
| pages   | Wiki pages. When using the pages descriptor, only the specified pages will be crawled for information. To get information from a child page, a child `pages` definition is required (This will also ensure that in the database, the `parent`/`app` of the child page will be set to the id of the parent page. The `pages` descriptor should only have navigation types as its immediate values. |
| spaces  | Wiki spaces. There should only ever be one `spaces` definition in the wiki configuration. |

##### Page Navigation

| Keyword | Description |
| ------- | ----------- |
| labels  | Find a wiki page which is labelled with the following label. |
| titles  | Find a wiki page with the following title. |

##### Page Information Retrieval

| Keyword         | Description |
| --------------- | ----------- |
| headings        | Gets information from the heading. |
| page            | Gets information from the entire page. |
| page_properties | Gets key-value pairs from the page properties macro. |
| panels          | Gets information from within a panel element in a wiki page. (For the APPLCTN space, the Overview panel will read up to the following words before stopping: `The application is accessible from these locations:`. | 