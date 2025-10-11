# Use a slim Python base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /sandbox

# Copy only the necessary parts of our application into the sandbox
# This includes the strategy framework, services, and models.
COPY ./app/trading_strategies /sandbox/app/trading_strategies
COPY ./app/services/backtesting_service.py /sandbox/app/services/
# Add any other necessary files for the backtester to run...

# Copy and install only the dependencies needed for backtesting
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# This is the script that the container will run when started.
COPY ./strategy_sandbox/run_sandbox_backtest.py .
ENTRYPOINT ["python", "run_sandbox_backtest.py"]