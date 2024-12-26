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


** Data Extraction **
    The ideal first task would be to create atleast 2 [S3](https://aws.amazon.com/s3/) buckets to start. One would be for storing the raw data that we get from the website. And the other would be for the Athena process to store query results. 

    Once we have the S3


