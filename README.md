# Dagster S3 ClickHouse Example

A Dagster demo showing how to load data into ClickHouse from S3. This demo uses a sensor to watch for new files in S3. When a new file is discovered, a partition is created and a run is launched to process the new data.

Video overview: https://www.loom.com/share/ad38c77796a24e439f33361849c512e9

## Getting started

### Python Dependencies

First, install the relevant Python packages:

```bash
pip install -e ".[dev]"
```

### ClickHouse Setup

Next, you will need to install and run ClickHouse. On a Mac:

```bash
curl https://clickhouse.com/ | sh
```

Once installed, run ClickHouse:

```bash
./clickhouse
```

In a separate terminal, create the table the Dagster jobs will populate:

```bash
./clickhouse client
CREATE TABLE dagster_demo (user String) ENGINE = MergeTree PRIMARY KEY (user);
```

### AWS Setup

Create an AWS S3 bucket. Create a folder in the bucket called `sensor_demo`. Then set the following environment variables:

```bash
export AWS_ACCESS_KEY_ID="AKEYID"
export AWS_SECRET_ACCESS_KEY="ASECRETKEY"
export AWS_PROFILE_NAME="AWSPROFILENAME"
export AWS_BUCKET="YOURBUCKET"
export AWS_REGION="YOURREGION"
```

### Run Dagster

In a terminal run:

```bash
dagster dev
```

Open http://localhost:3000 with your browser to see the project. Turn on the `my_s3_sensor` and the `my_mac_notify_on_run_success` sensors. Upload a file from `sample_data` to your s3 bucket in the `sensor_demo` folder. The sensor will launch a run to process the file. The `raw_data` asset will include a partition for each file uploaded to your s3 bucket. You can manually re-run a partition: select the `raw_data` asset, click Materialize,  select a partition, and click run. Successful runs will trigger a Mac notification as an example of a custom alert.

