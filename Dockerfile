# Base our container on the slim version of the official Python runtime.
FROM python:3.12.0a2-slim-bullseye

# The environment variable ensures that the python output is set straight
# to the terminal without buffering it first
ENV PYTHONUNBUFFERED 1

# create root directory for our project in the container and CD to it.
RUN mkdir /filebrowser
WORKDIR /filebrowser

# Copy the current directory contents into the container
ADD . /filebrowser/

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt
