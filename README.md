# Serverless Data Extraction and Transformation with Visualization
This project was done to look at extracting Stock data from the Polygon Stock Website and performing Data engineering processes on it, for storage and final visulaization on a Grafana Dashboard.

The data was pulled from [Polygon Stock Data](https://polygon.io/). Specificially the [aggregate bars](https://polygon.io/docs/stocks/get_v2_aggs_ticker__stocksticker__range__multiplier___timespan___from___to) which gives lot of useful information on a Stock over a date range in custom Window sizes

| Process | Tools |
| ----------- | ----------- |
| Data Extraction | AWS Lamda, AWS Kinesis Firehose, Amazon S3 |
| Data Transformation and Load | AWS Glue Crawler, AWS Glue ETL Jobs and Workflow, AWS Athena |
| Dashboarding and Misc | Amazon IAM, Grafana |

Lets deep dive into more details.

Now, what is Serverless Data Engineering. It is a is a method of collecting, transforming, and preparing data for analysis and decision-making using serverless technologies. It's a paradigm shift that allows data engineers to focus on developing data pipelines and applications without managing servers.

We are using different AWS technologies to achieve our goal here. Several key data engineering aspect utilized here include:
- Extracting data from a public website using secret keys assigned with the ability to store the Key in a vault
- Data extracted is then transformed from a JSON format to a Python understandable dictonary format and required elements are taken
- It is then fed to a process (AWS Kinesis Firehose) that listens to this data and stores it into a data store
- A crawler process would then identify the schema for the data in the storage, and create data catalog entries for it
- For ease of processing and performance, we conert the data into a [Parquet](https://www.databricks.com/glossary/what-is-parquet#:~:text=Apache%20Parquet%20is%20an%20open,handle%20complex%20data%20in%20bulk.) format
- Workflows would then run on demand which would look at the data, perform quality checks, remove any existing entries in the final tables, create new tables to store the data and finally store the data in the final Parquet format partioned for performance rationale.

The data flow is shown diagrammatically below. We will go into more details after this.

![AWS_DE_Project_Abe_Dec2024](https://github.com/user-attachments/assets/b914dabb-2181-4322-b8c7-3f5f590981b9)


## Data Extraction

The ideal first task would be to create atleast 2 [S3](https://aws.amazon.com/s3/) buckets to start. One would be for storing the raw data that we get from the website. And the other would be for the Athena process to store query results. 

We start first by creating a [AWS Lambda](https://aws.amazon.com/pm/lambda/?gclid=CjwKCAiAmrS7BhBJEiwAei59i5Q5rDOf1tv5NMyufZMunCcH-AqubZ2Nu-d-5eOEn1H8-tfsvh6zyRoCvYMQAvD_BwE&trk=73f686c8-9606-40ad-852f-7b2bcafa68fe&sc_channel=ps&ef_id=CjwKCAiAmrS7BhBJEiwAei59i5Q5rDOf1tv5NMyufZMunCcH-AqubZ2Nu-d-5eOEn1H8-tfsvh6zyRoCvYMQAvD_BwE:G:s&s_kwcid=AL!4422!3!651212652666!e!!g!!lambda!909122559!45462427876) function that reads data from the website and then feeds it to a AWS Kinesis Firehose process which then stores it into S3.

There are several aspects of configuration here which are important
- The Lambda Python code is available in the codes folder. I have looked to extract data for Google and Meta Tickers from July 1, 2025 till Dec 15th, 2025. About 6 months worth of data. The Polygon website needs api key to access the data. A key can be easily created, and I used the [AWS Secrets Manager](https://docs.aws.amazon.com/secretsmanager/latest/userguide/intro.html) to store the key and to be able to retrieve the key via Code and use it in the lambda function. Modularization in action ! I had to go several iterations before getting the code to work, while using Secrets Manager, but once you get the feel of what needs to be done, its straight forward
- [AWS Kinesis Firehose] is able to stream data from a source in batches or based on time limits and then send it to a Destination like S3. We used configuration of looking at a 5 MB Buffer Size or 60 secconds interval, before which the data is written to S3. This is an important configuration, since if we are dealing with data streams of either a continuous duration or infrequent ones but of larger sizes. The images folder has screenshots of how the config was setup.
  
  ![Kinesis](https://github.com/user-attachments/assets/ae61fbbe-60ff-4799-805d-ab0cf72b60ef)

- Eventually, the data is written into S3. We can see that S3 create a nested folder structure based on Year, Month, Date and Hour of data load. The file could actually be downloaded and we can view the data in a dictionary format (via Notebook or other Text Edit tools).
    
![S3](https://github.com/user-attachments/assets/0dc9b0c2-525c-47c8-a3c2-2438fdf44942)

    


