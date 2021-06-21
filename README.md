# Tsdat AWS Pipeline Template

This project template contains source code and supporting files for running multiple Tsdat pipelines via a single
serverless (i.e., lambda) application that you can deploy with the AWS SAM CLI. It includes the following files and folders:

- lambda_function - Code for the application's Lambda function and Project Dockerfile.  The lambda function can run
multiple pipelines as defined under the pipelines subfolder.  Each pipeline's code is contained in a further 
subfolder (e.g., lambda_function/pipelines/a2e_buoy_ingest).  You will need to create a folder for each pipeline that
you would like to run via this lambda template. The lambda_function/pipelines/runner.py class contains a map of
regular expressions which are used to map file names of a certain pattern to the pipeline and config files
that will be used to process that specific file.  The regular expressions will need to be updated to work with your
input file name patterns.
- data - Sample data to use for running tests local
- tests - Unit tests for the application code. `tests/test_pipeline.py` is used to run unit tests on your local filesystem.
Anyone can run the local filesystem tests.  `tests/test_lambda_function.py` is used to run unit tests against a test
S3 bucket.  You will need an AWS account and permissions to write to the test bucket in order to run the AWS unit tests.
- template.yaml - A template that defines the application's AWS resources that will be created/managed in a single
software stack via AWS Cloud Formation.  This template defines several AWS resources including Lambda functions,
input/output S3 buckets, and event triggers.  You should modify this template to create the appropriate resources 
needed for your AWS environment.
- samconfig.tomal - A config file containing variables specific to the deployment such as input/output bucket names,
stack name, and the logging level to use.

## Prerequisites
Anyone can edit pipeline code in this template, however the following are required in order to deploy your 
pipeline to AWS:

### 1) Create an AWS account.
This is necessary for admins who will deploy your application to AWS.  Each organization may have different policies for
creating new project accounts on AWS.  Please contact your local AWS administrator for assistance.

### 2) Configure IAM permissions for your acount.
Any user who will use this template to deploy resources to AWS must at least have the **Power User** role. Please 
contact your local AWS administrator for assistance.

### 3) Create an Amazon Elastic Container Registry (ECR) repository 
[Create an ECR repository](https://docs.aws.amazon.com/AmazonECR/latest/userguide/repository-create.html) where your lambda
Docker image will be deployed.

### 4) Install Docker
Required to build the AWS Lambda image. [Install Docker community edition](https://hub.docker.com/search/?type=edition&offering=community)

### 5) Install AWS CLI
Required to deploy the software stack defined in template.yaml.  [Install AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)

### 6) Install AWS SAM CLI
Required to deploy the software stack defined in template.yaml
The Serverless Application Model Command Line Interface (SAM CLI) is an extension of the AWS CLI that
 adds functionality for building and testing Lambda applications. It uses Docker to run your functions in an Amazon
 Linux environment that matches Lambda. It can also emulate your application's build environment and API.

[Install the SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)

### 6) Install Python & Tsdat
You will need Python for local testing and development - [Python 3 installed](https://www.python.org/downloads/)
You will also need Tsdat:
```bash
pip install tsdat
```

## Building your lambda function 
Use the `sam build` command to build your lambda function for deployment.

```bash
$ sam build
```

The SAM CLI builds a docker image from a Dockerfile, copies the source of your application inside the Docker image,
and then installs dependencies defined in `lambda_function/requirements.txt` 
inside the docker image. The processed template file is saved in the `.aws-sam/build` folder.


## Deploying your lambda function for the first time
To deploy your application for the first time, run the following in your shell:

```bash
sam deploy --guided
```

This will package and deploy your application to AWS, with a series of prompts asking for different parameter values.
The default values are shown in brackets [].  If you just hit Enter without typing a different value, the default
value will be used.  All of the default values will work out of the box except the Image Repository.  **You must paste
the URI for the ECR image repository created in Step #3 above**.  Each of the prompts are decribed in more detail below:

* **Stack Name**: The name of the stack to deploy to CloudFormation. This should be unique to your account and region, 
and a good starting point would be something matching your project name.
* **AWS Region**: The AWS region you want to deploy your app to.
* **Source Bucket**: The name of the S3 bucket where incoming raw files will be placed to trigger the pipeline.  Note
that this stack deployment WILL CREATE THIS BUCKET FOR YOU, so **the name must not already be in use**.
* **DestinationBucket**: The name of a different S3 bucket where the outputs of the tdat pipeline will be placed.   Note
that this stack deployment WILL CREATE THIS BUCKET FOR YOU, so the **name must not already be in use**.
* **LoggingLevel**: The logging level that will be used for python logging statements which get written to the lambda
function's CloudWatch logs.
* **Image Repository for LambdaFunction**: A URI for the ECR image repository that will be used to store your function's 
Docker image.  For example, `332883119153.dkr.ecr.us-west-2.amazonaws.com/a2e-tsdat-test`
* **Confirm changes before deploy**: If set to yes, any change sets will be shown to you before execution for manual review.
 If set to no, the AWS SAM CLI will automatically deploy application changes.
* **Allow SAM CLI IAM role creation**: Many AWS SAM templates, including this example, create AWS IAM roles required for the 
AWS Lambda function(s) included to access AWS services. By default, these are scoped down to minimum required permissions. 
To deploy an AWS CloudFormation stack which creates or modified IAM roles, the `CAPABILITY_IAM` value for `capabilities` must be provided. 
If permission isn't provided through this prompt, to deploy this example you must explicitly pass `--capabilities CAPABILITY_IAM` to 
the `sam deploy` command.
* **Save arguments to samconfig.toml**: If set to yes, your choices will be saved to a configuration file inside the project, so that in the future you can just re-run `sam deploy` without parameters to deploy changes to your application.

An Example guided deployment is shown below:

```bash
$ sam deploy --guided

Configuring SAM deploy
======================

        Looking for config file [samconfig.toml] :  Found
        Reading default arguments  :  Success

        Setting default arguments for 'sam deploy'
        =========================================
        Stack Name [tsdat-pipeline-stack]:
        AWS Region [us-west-2]:
        Parameter SourceBucket [tsdat-pipeline-inputs]:
        Parameter DestinationBucket [tsdat-pipeline-outputs]:
        Parameter LoggingLevel [DEBUG]:
        Image Repository for LambdaFunction [332883119153.dkr.ecr.us-west-2.amazonaws.com/a2e-tsdat-test]:
          lambdafunction:python3.8-v1 to be pushed to 332883119153.dkr.ecr.us-west-2.amazonaws.com/a2e-tsdat-test:lambdafunction-4bdc10a8a50a-python3.8-v1

        #Shows you resources changes to be deployed and require a 'Y' to initiate deploy
        Confirm changes before deploy [Y/n]: Y
        #SAM needs permission to be able to create roles to connect to the resources in your template
        Allow SAM CLI IAM role creation [Y/n]: Y
        Save arguments to configuration file [Y/n]: Y
        SAM configuration file [samconfig.toml]:
        SAM configuration environment [default]:
```


## Deploying your lambda function
Once you have used `sam deploy --guided` to update your samconfig.toml file the first time, you can subsequently deploy with the `sam deploy` command.

```bash
$ sam deploy
```
This will package and deploy your built application template to AWS.


## Using Your Pipeline on AWS
Once your pipeline has been deployed, you can trigger it by simply placing raw files into the Source Bucket you specified
during deployment.


## Fetch, tail, and filter Lambda function CloudWatch logs

To view/filter logs for your lambda function, you can use the
[Amazon CloudWatch](https://docs.aws.amazon.com/cloudwatch/index.html) user interface.

Alternatively, to simplify troubleshooting, SAM CLI has a command called `sam logs`. `sam logs` lets you 
fetch logs generated by your deployed Lambda function from the command line. In addition to printing the logs on the
 terminal, this command has several nifty features to help you quickly find errors.

Assuming you used the default stack name, to tail your pipeline logs, you can run this command:

```bash
$ sam logs -n LambdaFunction --stack-name tsdat-pipeline-stack --tail
```

You can find more information and examples about filtering Lambda function logs in the 
[SAM CLI Documentation](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-logging.html).

## Running Local Unit Tests (no container)

For initial pipeline development, it's easier to test your code locally without involving the lambda container.  Tests are defined in the `tests` 
folder in this project.  `tests/test_pipeline.py` is used to run unit tests to test your pipeline on your local filesystem.
Anyone can run the local filesystem tests - an AWS account or Docker is not required.

`tests/test_lambda_function.py` is used to run unit tests against a test
S3 bucket.  You will need an AWS account and permissions to write to the test bucket in order to run the AWS unit tests.

The `tests/events` folder contains simulated S3 bucket events that are used for running the pipeline tests against
an AWS S3 bucket.  In order to run  `test_lambda_function.py`, you will need to update the events to match your AWS
test data that should be deposited in a bucket for which you have read permissions.  Specifically, you will need to
update the bucket name property and object key property to match your specific test files as shown in the following
snippet from an event.json file.

```json
{
      "s3": {
        "s3SchemaVersion": "1.0",
        "configurationId": "4586d195-b484-464c-97f8-027348232818",
        "bucket": {
          "name": "a2e-tsdat-test",
          "ownerIdentity": {
            "principalId": "A21WSIO2BY6RXE"
          },
          "arn": "arn:aws:s3:::a2e-tsdat-test"
        },
        "object": {
          "key": "a2e_buoy_ingest/humboldt/buoy.z05.00.20201201.000000.zip",
          "size": 3679233,
          "eTag": "84703366a2bac7da56749b6cdbe37de1",
          "sequencer": "00606E62D96731561E"
        }
      }
}

```

## Running Local Tests via Docker Container
You may also want to test your pipeline locally by running inside the same lambda container that will be used on AWS.
To do this, you will need to have Docker installed on your machine.  Follow these steps to run your lambda container locally:

1. Upload the file you want to test to a test S3 bucket.
2. Create a json event for your test file and put it under the tests/events folder for the appropriate pipeline and location.  See `tests/events/a2e_imu_ingest/morro/s3-event.json` as an example.  You will need to change the S3 bucket name and S3 key to point to the correct file.
3. Use SAM to build and run the pipeline:
    ```bash
    sam build 
    sam local invoke tsdat-pipeline-lambda --event tests/events/a2e_imu_ingest/morro/s3-event.json 
    ```

## Cleanup

To undeploy your lambda function, use the AWS CLI. Assuming you used the default stack name provided by this template,
you can run the following:

```bash
aws cloudformation delete-stack --stack-name tsdat-pipeline-stack
```

**-----> NOTE: You MUST make sure that both your Source Bucket and Destination Bucket are completely empty or else you
will not be able to delete your stack.**

.

------------------------------------------------------------------------------------------------------------------------------
## ADVANCED:  Further customizing your application stack
This application template uses AWS Serverless Application Model (AWS SAM) to define application resources that will
be created automatically on AWS by the deploy command.
AWS SAM is an extension of AWS CloudFormation with a simpler syntax for configuring common serverless application 
resources such as functions, triggers, and APIs.
See the [AWS SAM developer guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html) for an 
introduction to SAM specification, the SAM CLI, and serverless application concepts.

By default, this template will create the following resources on AWS:
```bash
CloudFormation stack changeset
---------------------------------------------------------------------------------------------------------------------------------------------
Operation                           LogicalResourceId                   ResourceType                        Replacement
---------------------------------------------------------------------------------------------------------------------------------------------
+ Add                               DestinationS3Bucket                 AWS::S3::Bucket                     N/A
+ Add                               LambdaFunctionFileUploadedPermiss   AWS::Lambda::Permission             N/A
                                    ion
+ Add                               LambdaFunctionRole                  AWS::IAM::Role                      N/A
+ Add                               LambdaFunction                      AWS::Lambda::Function               N/A
+ Add                               SourceS3Bucket                      AWS::S3::Bucket                     N/A
---------------------------------------------------------------------------------------------------------------------------------------------
```

This should be adequate for most deployments, but in some cases you may need to change the configuration.  Here are a couple
of examples:

1. You need to trigger the pipeline from an AWS notification service message instead of from files being placed in the Source Bucket.
2. You need to trigger the pipeline from an existing S3 bucket that was not created by this template.

If you need to modify this template, it will require an in-depth knowledge of the [SAM specification](https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md),
and the [AWS CloudFormation](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-template-resource-type-ref.html)
resource types.  Contact your local AWS expert for assistance.

