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

## Modes of Operation
There are two modes of operation for the capsule application.
(Other than the below modes, a change to the configuration file will cause a full recheck to occur, this can take some
time).

### Full Delta Sync
In this mode, all pages on the wiki are rechecked to ensure that they meet the criteria set out in the config file.
To enable this mode, set the `--recheck-pages-meet-criteria` flag when running the main application.
(See Command Line Arguments section for more details).

### Half Delta Sync
In this mode, the application will only perform delta updates on pages that it currently knows about/that are stored in
the local database. This means that new pages added to the wiki will not be synced. Also, pages that no longer meet the
criteria set out in the config file will not be removed.

### Recommended Mode of Operation
It is recommended to run the application overnight for a Full Delta Sync (15 minutes) as this mode of operation takes a much longer time
than the Half Delta Sync. Running the below configuration file takes an average of 5 minutes on a Half Delta Sync, so this
can be run more often.

## Usage Notes
The following are important usage notes for the capsule application:

- Pages that are to be retrieved from the wiki should be child pages of the space Home. This is due to the fact that pages
are undiscoverable if they exist in a space but are not a child of the space Home.
- Linking in the configuration file must be correctly written as these are parsed in the Confluence API return `_links`
section and will be undiscoverable otherwise.
- Heading/Title matching only supports full text matches i.e. no regex.

### Command Line Arguments

The application supports the following command line arguments:

| Argument                 | Description |
| ------------------------ | ----------- |
| --recheck-pages-meet-criteria | This argument forces the database to refresh all pages and re-check that all current pages meet the labels/titles provided. | 

## Generating Documentation
The application supports documentation through Sphinx. To generate the Documentation run `make html`. Currently the
only way to do this is through the `Makefile`.

## Configuration
The configuration file is written in YAML. Currently the capsule application only supports a file in the application
directory named `config.yaml`.

### Example Configuration

```
confluence:
  host: https://wiki.auckland.ac.nz
  username:
  password:

mysql:
  host: 127.0.0.1
  port: 3306
  database: capsule
  username:
  password:
  wiki_table_prefix: wiki

logging:
  level: INFO

wiki:
  spaces:
    APPLCTN:
      pages:
        labels:
          application:
            panels:
              - Overview
              - Roadmap
              - Infrastructure
            page_properties:
              - inv_item_info
              - itil_stakeholders
              - nfr
            url:
              - tinyui
              - webui
            pages:
              labels:
                support_model:
                  page_properties:
                    - support_model
                    - support_tiers
                  url:
                    - webui
                inv_architecture_overview:
                  page_properties:
                    - inv_architecture_info
                  url:
                    - webui

    REFARCH:
      pages:
        titles:
          Reference Architecture:
            pages:
              titles:
                Information Architecture:
                  pages:
                    titles:
                      Information Entities:
                        pages:
                          labels:
                            entity_description:
                              page_properties:
                                - entity_description
                                - entity_caudit
                Technology Architecture:
                  pages:
                    labels:
                      service-area-metadata:
                        headings:
                          $ref: '#/schemas/REFARCH/service-area/headings'
                        pages:
                          labels:
                            domain-metadata:
                              headings:
                                $ref: '#/schemas/REFARCH/domain-brick-element/headings'
                              pages:
                                labels:
                                  brick-metadata:
                                    headings:
                                      $ref: '#/schemas/REFARCH/domain-brick-element/headings'
                                    pages:
                                      labels:
                                        element-metadata:
                                          headings:
                                            $ref: '#/schemas/REFARCH/domain-brick-element/headings'
schemas:
  REFARCH:
    service-area:
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
    domain-brick-element:
      headings:
        - Overview
        - Principles
        - Standards
        - Guidelines
        - Security
        - Monitoring
        - Resilience
        - Recovery
        - Future

```
### Logging Configuration

The application supports the following levels of logging:
 - CRITICAL
 - ERROR
 - WARNING
 - INFO
 - DEBUG
 - NOTSET

### Wiki Configuration

The example configuration above contains a configuration definition for `wiki`. This configures the capsule application
so that it knows where and what information the application is to retrieve. The  `wiki` configuration adheres to the
following design guideline.

```
wiki:
  spaces:
    [LIST OF SPACE NAMES]:
      pages:
        [PAGE NAVIGATION TYPES]:
          [Page NAVIGATION VALUE]:
            [PAGE INFORMATION RETRIEVAL TYPE]:
              - [PAGE INFORMATION RETRIEVAL VALUE]
```

#### Wiki Descriptors

| Keyword | Description |
| ------- | ----------- |
| pages   | Wiki pages. When using the pages descriptor, only the specified pages will be crawled for information. To get information from a child page, a child `pages` definition is required (This will also ensure that in the database, the `parent`/`app` of the child page will be set to the id of the parent page. The `pages` descriptor should only have navigation types as its immediate values. |
| spaces  | Wiki spaces. There should only ever be one `spaces` definition in the wiki configuration. |

##### Page Navigation Types

| Keyword | Description |
| ------- | ----------- |
| labels  | Find a wiki page which is labelled with the following label. |
| titles  | Find a wiki page with the following title. |

##### Page Information Retrieval Type

| Keyword         | Description |
| --------------- | ----------- |
| headings        | Gets information from the heading. |
| page            | Gets information from the entire page. |
| page_properties | Gets key-value pairs from the page properties macro. |
| panels          | Gets information from within a panel element in a wiki page. (For the APPLCTN space, the Overview panel will read up to the following words before stopping: `The application is accessible from these locations:`. | 
| url             | Retrieves URL information about a page. Sub options are `tinyui` and `webui`. 

### Using $ref

The configuration file supports the use of the `$ref` keyword for reusable configuration elements.

To reference a definition, use the $ref keyword:

`$ref: 'reference to definition'`

This works in a similar way to how Swagger implements the `$ref` tag. Please see their 
[documentation](https://swagger.io/docs/specification/using-ref/) for more details. Currently capsule is only able to
reference definitions within the current configuration document.

## TODO:

~~1. Fix view joining information.~~
~~2. Add Janes additional fields to configuration file.~~
3. Change how the application works by allowing a config file to be passed as a parameter (use one in directory if not present).
4. Make settings.py a configparser and return the config file to the function that called it.
5. Change how parameters work i.e. they should be called —half-sync —full-sync —bigquery.
6. Write bigquery/datastore script to push specific views to bigquery/datastore. Script should both be callable as a single script and as an extension of capsule application. The config file will look like: 
    ```
    bigquery/datastore:
      user: 
      pass: 
      tables:
       - wiki_app_info_full
    ``
7. Add —version/-v to command line options.
8. Update application inventory script to reflect these changes.
9. Fix database prefix.
10. Test the application configuration for spaces that don't exist.
11. Change how information gets delete from the database. These should not be committed until an update is completed and should be completed at the same time.
12. Investigate null applications (e.g. Gallagher Command Center).

