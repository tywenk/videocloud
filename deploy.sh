zip main.zip main.py
aws lambda update-function-code --function-name videocloud-fastapi --zip-file fileb://main.zip 
rm main.zip