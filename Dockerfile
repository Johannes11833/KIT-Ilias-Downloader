# set base image (host OS)
FROM python:3.11

# install rclone
RUN apt-get update && apt install rclone -y

# set the working directory in the container
WORKDIR /code

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD [ "python", "main.py" ]
