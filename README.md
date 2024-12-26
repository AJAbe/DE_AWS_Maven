# Serverless Data Extraction and Transformation with Dashboarding
This project was done to look at extracting Stock data from the Polygon Stock Website and performing Data engineering processes on it, for storage and final visulaization on a Grafana Dashboard.
[Polygon Stock Data](https://polygon.io/). Specificially the [aggregate bars] URL which gives lot of useful information on a Stock over a date range in custom Window sizes

|Data Extraction| AWS Lamda, AWS Kinesis Firehose, Amazon S3|
|Data Transformation and Load| AWS Glue Crawler, AWS Glue ETL Jobs and Workflow, AWS Athena|
