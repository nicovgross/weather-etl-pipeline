from main import run_pipeline

def lambda_handler(event, context):
    run_pipeline()

    return {
        "statusCode": 200,
        "body": "Pipeline executed successfully"
    }