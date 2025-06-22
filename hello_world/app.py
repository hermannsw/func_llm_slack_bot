import json
import os
import requests


def lambda_handler(event, context):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "hello world",
        }),
    }


def challenge_handler(event, context):
    """
    Lambda handler for /challenge endpoint

    Handles different Slack event types:
    - url_verification: Returns the challenge string
    - app_mention: Prepares for future app mention handling
    """
    try:
        # Parse the body of the event
        body = json.loads(event.get('body', '{}'))

        # Check the event type
        if body.get('type') == 'event_callback':
            event_type = body.get('event', {}).get('type')

            # URL Verification
            if event_type == 'url_verification':
                challenge = body.get('challenge', '')
                return {
                    "statusCode": 200,
                    "body": challenge
                }

            # App Mention
            elif event_type == 'app_mention':
                try:
                    # Send request to inhouse-flugel API
                    llm_result = requests.post(
                        os.environ.get('LLM_API_URL'),
                        headers={
                            'Authorization': '',  # Empty as specified
                            'Content-Type': 'application/json'
                        },
                        json={
                            "application_id": 3550, 
                            "stream": False, 
                            "messages": [
                                {
                                    "role": "user", 
                                    "contents": [
                                        {
                                            "type": "text",
                                            "content": body['event']['blocks'][0]['elements'][0]['elements'][1]['text']
                                        }
                                    ]
                                }
                            ]
                        }
                    )
                    llm_response_body = json.loads(llm_result.text)

                    # Send Slack webhook request with LLM result
                    webhook_url = os.environ.get('SLACK_WEBHOOK_URL')
                    if webhook_url:
                        try:
                            response = requests.post(webhook_url, json={
                                "text": llm_response_body['reply'][0]['contents'][0]['content']
                            })
                            response.raise_for_status()  # Raise an exception for HTTP errors
                        except Exception as e:
                            print(f"Error sending Slack webhook: {e}")

                    return {
                        "statusCode": 200,
                        "body": json.dumps({
                            "message": "App mention processed",
                            "llm_result": llm_result,
                            "event": body.get('event', {})
                        })
                    }
                except Exception as e:
                    print(f"Error processing app mention: {e}")
                    return {
                        "statusCode": 500,
                        "body": json.dumps({"error": str(e)})
                    }

        # If not a recognized event type, return an error
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Unrecognized event type"})
        }

    except json.JSONDecodeError:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Invalid JSON"})
        }
