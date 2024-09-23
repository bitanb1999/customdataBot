# STEP 1: Install Python base image
FROM python:3.9-slim

# Step 2: Add requirements.txt file 
COPY requirements.txt /requirements.txt
#
# Step 3:  Install required pyhton dependencies from requirements file
RUN pip install -r requirements.txt

# Step 4: Copy source code in the current directory to the container
ADD . /app

COPY app.py ./app.py

# Step 5: Install git 
RUN apt-get update && apt-get install -y \
    build-essential \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*


# Step 6: Set working directory to previously added app directory
WORKDIR /app

# # Step 7: Expose the port is running on
EXPOSE 8501

# Step 8: Run the application
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
