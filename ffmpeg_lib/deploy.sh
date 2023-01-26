zip -j ramen.zip ./stream/lambda_function.py
aws lambda update-function-code --function-name alfredo-shared-ramen --zip-file fileb://ramen.zip 
rm ramen.zip
