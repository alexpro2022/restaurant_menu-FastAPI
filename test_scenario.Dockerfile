FROM python:3.10-slim
WORKDIR /main
COPY requirements.txt .
RUN python -m pip install --upgrade pip && \
    pip install -r requirements.txt --no-cache-dir
COPY . .
CMD ["pytest", "tests/test_scenario.py"]
