FROM ubuntu:14.04

# Set the file maintainer (your name - the file's author)
MAINTAINER SeungJu SJ Lee

# Set env variables used in this Dockerfile
ENV PYTHON_ENV=production

# Install Python Setuptools
# Update the default application repository sources list
RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y python python-pip pypy libxml2-dev libxslt1-dev python-dev

# Create a directory
RUN mkdir src

# Add and install Python modules
ADD requirements.txt /src/requirements.txt
RUN cd /src; pip_pypy install -r requirements.txt

# Bundle app source
ADD . /src

# Expose
EXPOSE  5000

# Change working directory
WORKDIR /src

# Create credentials.json
RUN echo "{\"CONSUMER_SECRET\": \"$CONSUMER_SECRET\", \"TOKEN\": \"$TOKEN\", \"CONSUMER_KEY\": \"$CONSUMER_KEY\", \"TOKEN_SECRET\": \"TOKEN_SECRET\"}" > credentials.list

# Run
CMD ["pypy", "post_request.py"]
