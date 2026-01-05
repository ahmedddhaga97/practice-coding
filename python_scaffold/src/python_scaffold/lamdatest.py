import os
import logging
import boto3
import pandas as pd
from pathlib import Path

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Local CSV->Parquet conversion (kept for local runs)
input_dir = Path(r"C:\\Work\\input")
output_dir = Path(r"C:\\Work\\output")

# Create output folder if not exists
output_dir.mkdir(parents=True, exist_ok=True)

for csv_file in input_dir.glob("*.csv"):
    print(f"Processing: {csv_file.name}")

    df = pd.read_csv(csv_file)

    parquet_file = output_dir / (csv_file.stem + ".parquet")
    df.to_parquet(
        parquet_file,
        engine="pyarrow",
        compression="snappy",
        index=False
    )

print("All CSV files converted to Parquet.")

# --- AWS Lambda S3 handler ---
s3 = boto3.client('s3')

def handler(event, context):
    """AWS Lambda handler triggered by S3 put/create events.

    Copies objects uploaded under the prefix `inputcsv/` to `outputpr/` in the same bucket.
    By default, the object is copied only. To delete the source object after copy (i.e. move),
    set the environment variable `MOVE_OBJECT` to `true`.
    """
    move_object = os.environ.get('MOVE_OBJECT', 'false').lower() == 'true'

    records = event.get('Records', [])
    for rec in records:
        try:
            s3_info = rec.get('s3', {})
            bucket = s3_info.get('bucket', {}).get('name')
            key = s3_info.get('object', {}).get('key')

            if not bucket or not key:
                logger.warning('Missing bucket or key in record: %s', rec)
                continue

            # Only handle objects under the inputcsv/ prefix
            prefix = 'inputcsv/'
            if not key.startswith(prefix):
                logger.info('Skipping key not under %s: %s', prefix, key)
                continue

            dest_key = key.replace(prefix, 'outputpr/', 1)

            copy_source = {'Bucket': bucket, 'Key': key}
            logger.info('Copying s3://%s/%s to s3://%s/%s', bucket, key, bucket, dest_key)

            s3.copy_object(Bucket=bucket, CopySource=copy_source, Key=dest_key)

            if move_object:
                logger.info('Deleting original object s3://%s/%s', bucket, key)
                s3.delete_object(Bucket=bucket, Key=key)

        except Exception as e:
            logger.exception('Error processing S3 record: %s', e)

    return {'status': 'completed'}


if __name__ == '__main__':
    print('Module run locally. The AWS Lambda handler is `handler(event, context)`.')
