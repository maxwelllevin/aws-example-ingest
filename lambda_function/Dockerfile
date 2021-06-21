#FROM public.ecr.aws/lambda/python:3.8
FROM tsdat/tsdat-lambda:0.2.4

COPY lambda_function.py requirements.txt ./
COPY pipelines ./pipelines

RUN python3.8 -m pip install -r requirements.txt -t .

# Command can be overwritten by providing a different command in the template directly.
CMD ["lambda_function.lambda_handler"]
