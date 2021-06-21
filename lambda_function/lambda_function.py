import json
import os
from pipelines.runner import run_pipeline
from typing import Dict
from urllib.parse import unquote_plus

from tsdat.io import S3Path
from pipelines.utils.log_helper import logger, log_exception


def get_s3_path(record: Dict):
    bucket_name = record['s3']['bucket']['name']
    bucket_path = unquote_plus(record['s3']['object']['key'])
    s3_path = S3Path(bucket_name, bucket_path)
    return s3_path


def set_env_vars():
    """-------------------------------------------------------------------
    Environment variables are used to set values in the pipelines'
    storage_config.yml file.  If running from a deployed lambda environment,
    then some of these environment variables will be set based upon the
    parameters in the deployment template.

    If running from a local test environment, these environment variables
    must be set in the unit test configuration.

    This method will make sure all values are set if not specified by
    external sources.
    -------------------------------------------------------------------"""

    # Name of storage bucket where output files are written
    bucket_name = os.environ['STORAGE_BUCKET']
    assert bucket_name

    # Logging level to use.  It must match
    logging_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
    os.environ['LOG_LEVEL'] = logging_level

    # Whether or not original input files should be kept after they are
    # done processing
    retain_input_files = os.environ.get('RETAIN_INPUT_FILES', 'False')
    os.environ['RETAIN_INPUT_FILES'] = retain_input_files

    # Storage
    storage_classname = os.environ.get('STORAGE_CLASSNAME', 'tsdat.io.AwsStorage')
    os.environ['STORAGE_CLASSNAME'] = storage_classname


def lambda_handler(event, context):
    """-------------------------------------------------------------------
    Lambda function to run a tsdat pipeline. Function will be triggered
    by an s3 event for an incoming raw data file.  The pipeline will
    process the raw file to standard format and save to a new s3 bucket.

    Args:
        event (Dict):     Dictionary of event parameters.
                          For tsdat, event will include the s3 file the triggered the event.
                          Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

        context (object): Lambda Context runtime methods and attributes
                          Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html
    -------------------------------------------------------------------"""

    # Make sure the default environment variables are set
    set_env_vars()

    # Configure the root logger
    logger.setLevel(os.environ['LOG_LEVEL'])

    # We combine all the request information into a single json object so it's easier to read in the CloudWatch logs!
    debug_info = json.dumps({
        "message": "Invoking lambda function",
        "environment": dict(os.environ),
        "event": event
    })
    logger.info(debug_info)

    try:
        input_files = []

        for record in event['Records']:
            # Get the AWS path to the raw file from the lambda event
            s3_path = get_s3_path(record)
            input_files.append(s3_path)

        deployment_mode = 'aws_dev'

        run_pipeline(input_files=input_files)

    except Exception as e:
        # This is only to catch for exceptions that happen outside the pipeline
        # as the pipeline runner will catch any pipeline exceptions.
        log_exception("Failed to invoke lambda function.")





