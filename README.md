# Complete Banking Domain Project

## Project Outline

### Day-1 :- Architecture & Data Ingestion Layer

### Architecture

Step 1 → Create Storage Account (ADLS Gen2) + 4 Containers
1.	Top search → type “Storage accounts” → click it
2.	Click + Create
3.	Fill exactly:
o	Resource group: azurebank-rg
o	Storage account name: azurebankstorage999 
o	Redundancy: Locally-redundant storage (LRS)
4.	Click Advanced tab → Check the box Enable hierarchical namespace (this makes it ADLS Gen2)
5.	Click Review → Create (wait 1–2 minutes)
6.	After created → click Go to resource
7. Left menu → Containers (under Data storage) 
8. Click + Container four times and create these exact names (all lowercase):
•	raw-transactions
•	raw-customers
•	raw-atm
•	raw-upi
9.	Public access level → Private → Create each one

    
Step 2 → Upload Random Banking Dataset

Step 3 → Create Service Bus + Queue
1.	Top search → “Service Bus” → click it
2.	Click + Create
3.	Fill:
o	Resource group: azurebank-rg
o	Namespace name: azurebank-sb 
4.	Click Review + create → Create 
5.	Click Go to resource
6.	Left menu → Queues → click + Queue
o	Name: ingestion-queue
o	Leave everything default → Create

 
Step 4 → Create Function App (Python)
1.	Top search → “Function App” → click it
2.	Click + Create
3.	Fill exactly:
o	Resource group: azurebank-rg
o	Function App name: azurebank-ingestion-func 
o	Publish: Code
o	Runtime stack: Python
4.	Click Review + create → Create 
5.	After created → click Go to resource

   
Step 5 → Create Event Grid Trigger Function 
1.	In your Function App → left menu → Functions → click + Create
2.	Choose:
o	Development environment: Develop in portal
o	Select a template: Azure Event Grid trigger
o	New function name: BlobCreatedTrigger → Click Create


Step 6 → Connect Event Grid to Your Function (Portal only)
1.	Go back to your Storage Account (azurebankstorage999…)
2.	Left menu → Events (under Data management)
3.	Click + Event Subscription
4.	Fill exactly:
o	Name: raw-containers-to-function
o	Event Types: Check only Blob Created
o	Endpoint type: Azure Function
o	Endpoint: Choose subscription → resource group → your Function App → BlobCreatedTrigger
5.	Click Create

   
Step 7 → FINAL TEST – Watch the magic happen
1.	Go to container raw-atm
2.	Upload the same atm_sample.csv again

# Flow of project day1

1. Source Systems (Simulated Banking Channels)
├── ATM Transactions          → CSV file (atm_sample.csv)
├── UPI Payments              → CSV file (upi_sample.csv)
└── Customer Master           → CSV file (customers_master.csv)

2. Landing Zone – Azure Data Lake Storage Gen2 (ADLS Gen2)
   Storage Account: azurebankstorage999… (Hierarchical namespace = Enabled)
   Containers created:
   ├─ raw-atm
   ├─ raw-upi
   ├─ raw-transactions
   └─ raw-customers
   → All sample files successfully uploaded

3. Event Capture – Azure Event Grid
   Event Subscription Name: raw-containers-to-function
   Trigger: Blob Created
   Filter: Subject begins with  /containers/raw-
   → Any new file in any raw-* container instantly fires an event

4. Real-Time Processor – Azure Functions (Python)
   Function App: azurebank-ingestion-func (Linux, Consumption)
   Function Name: BlobCreatedTrigger (Event Grid trigger)
   What it does the moment a file lands:
   ├─ Logs the event
   ├─ Extracts full blob URL and container name
   ├─ Builds JSON message
   └─ Pushes message to Service Bus queue

5. Orchestration Queue – Azure Service Bus
   Namespace: azurebank-sb (Standard tier)
   Queue: ingestion-queue
   → Every uploaded file results in exactly ONE message sitting here
     (you can see active message count = 1 after test upload)

6. End-to-End Test Flow (You already executed this successfully)
   1. Upload atm_sample.csv → raw-atm container
   2. Event Grid instantly detects Blob Created
   3. BlobCreatedTrigger function executes (visible in Monitor → Logs)
   4. Function pushes JSON message to ingestion-queue
   5. Service Bus queue shows Active message count = 1

Result after Day 1
