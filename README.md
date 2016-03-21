# Warning!!
This project no longer works. Yelp noticed the crawling server and blocked it. If you want to still use it for personal purposes, try Selenium.


# for dev OSX
virtualenv .ven
source .venv/bin/activate
pip install -r requirements.txt
python post_request.py
Send a HTTP request to port 5000 from frontend

# for production Ubuntu 14.04 Dockerfile
sudo docker build -t imhungry_api_img .
sudo docker run -name imhungry_api_instance \
                -p 5000:5000 \
                -e CONSUMER_SECRET='enter yelp consumer secret' \
                -e TOKEN='enter yelp token'
                -e CONSUMER_KEY='enter yelp consumer key'
                -e TOKEN_SECRET='enter yelp token secret'
                -i -t imhungry_api_img
TODO: Handle logs and make the contents of credentials.json as input parameters of docker container

# for production (Vagrant Ubuntu 14.04 hashicorp/precise64) with pypy
vagrant up && vagrant ssh

# for production (Ubuntu 14.04) with pypy
sudo apt-get update
sudo apt-get install -y build-essential
sudo apt-get install -y python-virtualenv
sudo apt-get install -y pypy
sudo apt-get install -y libxml2-dev libxslt1-dev python-dev
virtualenv -p /usr/bin/pypy .venv
source .venv/bin/activate
pip install -r requirement_prod.txt
python post_request.py
