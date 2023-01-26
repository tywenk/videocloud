# Basic FastAPI AWS Lambda

Base on this repo: [https://github.com/pixegami/fastapi-aws-lambda]

## Deploying FastAPI to AWS Lambda

We'll need to modify the API so that it has a Lambda handler. But after that, we can zip up the dependencies like this:

Make or update the `requirements.txt` file:

`conda list --export > requirements.txt`

OR

`pip list --format=freeze > requirements.txt`

Then we'll need to install the dependencies into a directory called `lib`:

`pip install -t lib -r requirements.txt`

Now you'll need to create a zip file where the FastAPI app and the dependencies are in the same closure.

`(cd lib; zip ../lambda_function.zip -r .)`

Now add our FastAPI files.

`zip lambda_function.zip -u main.py`
`zip lambda_function.zip -u aws_client.py`
