# set base image (host OS)
FROM python:3.11

# install curl
RUN apt-get update && apt install rclone -y

# set the working directory in the container
WORKDIR /code

# copy the dependencies file to the working directory
COPY requirements.txt .

# install dependencies
RUN pip install -r requirements.txt

# copy the content of the local src directory to the working directory
COPY . .

# command to run on container start
CMD [ "python", "main.py" ]