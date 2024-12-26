# Serverless Data Extraction and Transformation with Visualization
This project was done to experiment on extracting Company Stock data from the Polygon Stock website and performing Data engineering processes on it, for storage and final visualization on a Grafana Dashboard.

The data was pulled from [Polygon Stock Data](https://polygon.io/). Specificially the [Daily Aggregated Data](https://polygon.io/docs/stocks/get_v2_aggs_ticker__stocksticker__range__multiplier___timespan___from___to) which gives lot of useful information on a Stock over a date range in custom Window sizes.

| Process | Tools |
| ----------- | ----------- |
| Data Extraction | AWS Lamda, AWS Kinesis Firehose, Amazon S3 |
| Data Transformation and Load | AWS Glue Crawler, AWS Glue Data Catalog, AWS Glue ETL Jobs and Workflow, AWS Athena |
| Dashboarding and Misc. | Amazon IAM, Grafana |

Lets deep dive into more details.

Now, what is Serverless Data Engineering ? It is a is a method of collecting, transforming, and preparing data for analysis and decision-making using serverless technologies. It's a paradigm shift that allows data engineers to focus on developing data pipelines and applications without managing servers. So in many ways, a mix of IaaS and SaaS.

We are using different AWS technologies to achieve our goal here. Several key data engineering aspect utilized include:
- Extracting data from a public website (Lambda) using secret keys assigned with the added ability to store the Key in a vault
- Data extracted being transformed from a JSON format to a Python dictionary format with the required elements
- Fed to a process (AWS Kinesis Firehose) that listens to this data and stores it into a data store (S3)
- A Crawler process would then identify the schema for the data in the storage, and create data catalog entries for it (Athena)
- For ease of processing and performance, we conert the data into a [Parquet](https://www.databricks.com/glossary/what-is-parquet#:~:text=Apache%20Parquet%20is%20an%20open,handle%20complex%20data%20in%20bulk.) format
- Workflows(Glue) would then run on demand which would look at the data, perform quality checks, remove any existing entries in the final tables, create new tables to store the data and finally store the data in the final Parquet format partioned for performance rationale.

The data flow is shown diagrammatically below. We will go into more details after this.

![AWS_DE_Project_Abe_Dec2024](https://github.com/user-attachments/assets/b914dabb-2181-4322-b8c7-3f5f590981b9)

## Data Extraction

The ideal first task would be to create atleast 2 [S3](https://aws.amazon.com/s3/) buckets to start. One would be for storing the raw data that we get from the website. And the other would be for the Athena process to store query results. We would need to create additional buckets (2 more) during the Workflow build stage.

We start first by creating an [AWS Lambda](https://aws.amazon.com/pm/lambda/?gclid=CjwKCAiAmrS7BhBJEiwAei59i5Q5rDOf1tv5NMyufZMunCcH-AqubZ2Nu-d-5eOEn1H8-tfsvh6zyRoCvYMQAvD_BwE&trk=73f686c8-9606-40ad-852f-7b2bcafa68fe&sc_channel=ps&ef_id=CjwKCAiAmrS7BhBJEiwAei59i5Q5rDOf1tv5NMyufZMunCcH-AqubZ2Nu-d-5eOEn1H8-tfsvh6zyRoCvYMQAvD_BwE:G:s&s_kwcid=AL!4422!3!651212652666!e!!g!!lambda!909122559!45462427876) function that reads data from the website and then feeds it to a AWS Kinesis Firehose process, which then stores it into S3.

There are several aspects of configuration here which are important
- The Lambda Python code is available in the /code folder. I have looked to extract data for Google and Meta Tickers from July 1, 2025 till Dec 15th, 2025. About 6 months worth of data. It picks the closing Stock Price for both Google and Meta as of the specific day. Data Elements that are used --> Ticker (GOOG or META), Closing Date, Closing Stock Value
- The Polygon website needs an API key to access the data. A key can be easily created from their Website, and I used the [AWS Secrets Manager](https://docs.aws.amazon.com/secretsmanager/latest/userguide/intro.html) to store the key and to be able to retrieve the key via Code and use it in the lambda function. I had to go several iterations before getting the code to work, while using Secrets Manager, but once you get the feel of what needs to be done, its straight forward
- [AWS Kinesis Firehose](https://aws.amazon.com/firehose/) is able to stream data from a source in batches or based on time limits and then send it to a destination like S3. We used configuration of either looking at a 5 MB Buffer Size or 60 secconds interval, before which the data is written to S3. This is an important configuration, if we are dealing with data streams of either a continuous duration or infrequent ones but of larger sizes. 
  
  ![Kinesis](https://github.com/user-attachments/assets/ae61fbbe-60ff-4799-805d-ab0cf72b60ef)

- Eventually, the data is written into S3. We can see that S3 create a nested folder structure based on Year, Month, Date and Hour of data load. The file could actually be downloaded and we can view the data in a dictionary format (via Notebook or other Text Edit tools).
    
![S3](https://github.com/user-attachments/assets/0dc9b0c2-525c-47c8-a3c2-2438fdf44942)

## Data Transformation and Load

Next we get into the more technical piece for the project. We have the data in the S3 layer. Remember, its still in the raw format. There could be data issues present. We need to perform quality checks and correct the data as needed.

But first, we need to inspect the data. That too, smartly, not spending a lot of time, defining the columns and data types. Enter AWS Crawler. We do that by using the [AWS Crawler](https://docs.aws.amazon.com/glue/latest/dg/add-crawler.html) job which inspects the schema of the dataset in S3 and then creates a Data Catalog within AWS Athena. And we can then query our data in [AWS Athena](https://aws.amazon.com/athena/). There isn't a lot to discuss on confuring the Crawler job, except to specify the source S3 location and the target database where we need to store the Data Catalog to. In essence, a table gets created which can be queried via Athena, though behind the scenes, it still querying the data in S3 using the schema details in the Catalog.

Now, comes the main part. [AWS Glue](https://aws.amazon.com/glue/) There are two main components of Glue that we will use here. One is the ETL Jobs part (Python files) and the other is the process to stitch them together - [Glue Workflows](https://docs.aws.amazon.com/glue/latest/dg/workflows_overview.html)

We start by creating 4 ETL Jobs that does the below functions
  - Delete any existing Parquet table with the same name as provided. We could remove and recreate any Buckets that exist with the same name
  - Insert new records in Parquet format
  - Perform Data Quality checks on the source data
  - Publish out the file
  - *The 4th step is more or less the piece where we can partition out the data from the main table after DQ checks based on attributes like month and year and store data in terms of having date / onth / year suffixes etc.*


The Workflow part is where the core part of the processing happens. 

As shown in the diagram below, each of the jobs created above is stitched together via Triggers in the Workflow module.The first trigger denotes the start of the Crawler job to create the raw Data Catalog from the S3 contents. And then we proceed with Data Quality checks. For the purpose of this specific use case, I just looked into validating if any Closing Stock value amount is null and if so, to fail the job. Post that, we write out the final contents into a new S3 folder (yes, this has to be created prior as mentioned above) and new tables (Catalog) within Athena. The final table is also partitioned via Month and Year (would help in performance), as well as the Table is Name suffixed with Date, Month and Year. Why is this good ? Well, loads across the day would sit in different tables based on how the S3 tables are built (again based on config from Firehose), but would eventually help in partitioning the data as needed, especially while investigating isues on which datasets have issues.

![Glue Workflow](https://github.com/user-attachments/assets/cc8b130d-1bfc-4f09-986c-6eec1e694741)

![Final Athena Table](https://github.com/user-attachments/assets/7cba6c25-3814-4915-8ce9-fbe5ab6ec6fa)

## Grafana Visualization

Finally, we expose the data onto a Grafana Dashboard. Grafana is not a AWS managed tool, though AWS has connectors to be able to connect to Grafana. There are different ways to connect to Grafana inclusing [AWS Managed Grafana Instance](https://aws.amazon.com/grafana/), but I used the [AWS Auth process](https://grafana.com/docs/grafana/latest/datasources/aws-cloudwatch/aws-authentication/) within Grafana. This would also entail creating a new Access Key ID - Key pair via [IAM - Users](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html).

Finally, I created a Dashboard that has two reports. One shows the daily closing stock value for both companies. And the other shows the Average for each company across the 6 month period

[Final Data Snapshot](https://abejabe.grafana.net/dashboard/snapshot/qJYVzvGEy1KbfMx7jdzflTQbo6tKxWvb)

## Alert - IAM Steps - Very Important

- Ensure the below Roles are assigned to ensure the data flow proceeds smooth and sound.
- As part of working with AWS Glue, there will be a standard role created (AWSGlueServiceRole). Ensure that it has permission to the below Policies
  - AmazonAthenaFullAccess
  - AmazonS3FullAccess
- The role created for the Lambda Service. It needs to have the AmazonKinesisFirehoseFullAccess Policy added to it. Additionally, if AWS Secrets Manager is beig used, have the SecretsManagerReadWrite Policy also added
- The Firehose role needs to have the AmazonS3FullAccess added.
- The Grafana user created would also need the AmazonAthenaFullAccess and AmazonS3FullAccess policies added

## Learnings and Next Steps

- During the Lambda Code development, I hadnt specifically coerced the Stock Value variable to be decimal. This caused the value to get stored as a String and eventually caused issues during viz. I had to work back via debugging to eventialluy fix it. Learning: ALways be sure of what data type, you expect the data to be in, before the stage of final table publish
- Understanding AWS Secrets Manager - Nothing specific to bring here, except I missed few aspects while coding, which were straightforward. There is boiler plate code that AWS provides, so just be sure to use that.
- Debugging IAM Access Roles and its interactions with various modules. Unfortunately, learnt it the hard way via the course as well as googling, but again worth the effort
- I would like to experiment a bit more with creating reports from Grafana. Especially pivoting on multiple dimensions (like showing Average each month per Ticker value). I was not able to get it working, so might want to check on it
- [AWS Event Bridge](https://aws.amazon.com/eventbridge/) : Lets say, we need the Lambda job to constantly listen to the WebSite on an interval and process data. Thats where Event Bridge comes in, and can be used to invoke the lmbda function on an interval. Might not be too relevant for this use case, but there are certainly scenarios where it could be useful to ensure the process picks up updates.
- I tried to experiment with [AWS SES]([ aws](https://aws.amazon.com/getting-started/hands-on/send-an-email-with-amazon-ses/) in order to configure outward emails during DQ job failure, but was not able to get it working. Probably for a later experiment.
- More in depth DQ procedures.

