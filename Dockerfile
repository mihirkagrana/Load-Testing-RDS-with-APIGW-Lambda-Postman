# Use a Python base image that matches the Lambda runtime
# For Python 3.9, you can use a base image close to the Lambda environment.
# 'public.ecr.aws/lambda/python:3.9' is a good choice as it's the official Lambda base image.
FROM public.ecr.aws/lambda/python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies from requirements.txt
# The --target flag installs packages into a specific directory, which is useful for zipping later.
RUN pip install -r requirements.txt --target /asset-output

# Copy your lambda function code into the container
COPY lambda_function.py /asset-output/

# This Dockerfile is for creating the zip, not directly running the Lambda,
# so we don't need a CMD or ENTRYPOINT for execution.
# The `/asset-output` directory will contain your lambda code and its dependencies.
