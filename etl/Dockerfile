FROM public.ecr.aws/lambda/python:3.10

WORKDIR ${LAMBDA_TASK_ROOT}

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY config/ ./config/
COPY scripts/ ./scripts/

ENV PYTHONPATH="${LAMBDA_TASK_ROOT}/src"

CMD ["lambda_handler.lambda_handler"]