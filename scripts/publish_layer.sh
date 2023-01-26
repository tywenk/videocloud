mkdir python
pip freeze --format=freeze > requirements.txt
pip install -t python -r requirements.txt
zip -r fastapi_layer.zip python
aws lambda publish-layer-version --layer-name fastapi_layer \
    --description "FastAPI and Mangum Layer" \
    --license-info "MIT" \
    --zip-file fileb://fastapi_layer.zip \
    --compatible-runtimes python3.9 \
    --compatible-architectures "arm64" "x86_64"
rm -rf python
rm fastapi_layer.zip