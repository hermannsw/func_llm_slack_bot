# llm_sam

## Deploy the sample application

```bash
sam build --use-container
sam deploy --guided
```

```bash
sam local start-api
curl http://localhost:3000/
```

```bash
sam logs -n HelloWorldFunction --stack-name "llm_sam" --tail
```

## Tests

```bash
pip install -r tests/requirements.txt --user
# unit test
python -m pytest tests/unit -v
# integration test, requiring deploying the stack first.
# Create the env variable AWS_SAM_STACK_NAME with the name of the stack we are testing
AWS_SAM_STACK_NAME="llm_sam" python -m pytest tests/integration -v
```

## Cleanup

```bash
sam delete --stack-name "llm_sam"
```
