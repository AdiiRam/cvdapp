## CVE Web App 

### Introduction 
The CVE Web App is a simple webapp used to either get the details of a specific CVE or a details of list of CVEs matching the specific query provided. 

### System Design
The overall system is split into 2 parts. Part 1 takes care of data preparation and migration. This happens either as a full load or incrementally. Part 2 serves as the webapp for the data gathered in Part 1. 

#### Part 1 : Data Preparation And Migration 
This system mainly takes care of fetching the list of CVEs from the database and adds them to a Mongo Collection. The current system supports 2 modes of execution : 
- Full Load 
- Incremental 

The full load mode is useful in cases where the whole collection of CVE is to be fetched and stored in the database. 
The incremental mode is useful in cases where the data is to be fetched and updated in an incremental fashion. 

#### Part 2 : Search App 
This system provides a simple way to search and query the data collected by the Part 1 System . The current system supports the following ways to get details of 1 or more CVEs 
- Get CVE By CVE ID 
- Get CVE By Base Score - Only Equality is supported 
- Get CVE By Last Modified in Last N Days - Accepts No of Days as input

### Code Organization 
The following table provides the list of source code files along with a small description of the same . 


|File Name|Short Description|
|---|---|
|constants.py|The constants and other configuration related params are declared here|
|dbutils.py|The DB Operations are present|
|cvdwrapper.py|Functionality for Part 1 System|
|webapp.py|Functionality for Part 2 System|
|incremental_mode.json|JSON File that stores the Last Run Time for incremental load
|requirements.txt|Dependencies listed here|

### Execution and Testing 
The followings steps can be followed to setup, execute and test the webapp. 

1. Using the config_template.ini , create a new file config.ini with all the configurations populated as per your requirements. 
Below table lists the configurations currently supported along with their expected usage 

|Config Group|Config Key|Acceptable Value|Description|
|---|---|---|---|
|Database|host||host path|
|Database|port||port number|
|Database|username||db user|
|Database|password||db password|
|Database|database||db name|
|Database|collection||db collection|
|LoadMode|mode|full or incremental|Type of data load to do|
|LoadMode|results_per_page|number between 1-2000|No of results per page|
|TestRun|enabled|yes or no|Whether using for Test purposes or not|
|TestRun|no_of_pages||how many pages to fetch|
|CVEAPI|base_api||the CVE API to use|

2. Environment Setup 
Setup the Environment with the dependencies mentioned in the requirements.txt installed. 

3. Loading of Initial Data to the Database . 
Before the Web App can be used, we need to prepopulate the database/collection with the cve fetched. For this , run the cvdwrapper.py . 

```
python3 cvdwrapper.py
```
**Points to note:**

a. If running for the first time , then set the mode to full. This will pull all the cve's and insert to the collection.

b. If collection is already present , then set the mode to incremental. This will pull the updated cve's which were modified since the last run. The last run will be stored locally in the file incremental_mode.json under the key 'lastrun'



4. Running the Web App Server 
Once the database is populated with the required CVE docs , the server can be started. 

```
uvicorn webapp:app 
```

5. Swagger Endpoint 
Once the server is up and running , you can view the SWagger UI and Docs by using the [endpoint](http://127.0.0.1:8000/docs#) 



