conda list --export > requirements.txt
pip install -t lib -r requirements.txt
zip lambda_function.zip -r lib/
zip lambda_function.zip -u main.py
zip lambda_function.zip -u aws_client.py
# aws lambda update-function-code --function-name videocloud-fastapi --zip-file fileb://lambda_function.zip 
# rm lambda_function.zip