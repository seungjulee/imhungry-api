# API Server for I'm Hungry - Your Local Food Porn
http://devpost.com/software/i-m-hungry

# Warning!!
This project no longer works. Yelp noticed the crawling server and blocked it. If you want to still use it for personal purposes, try Selenium. It was built over one weekend, and didn't
have time to go through thorough test.

## For Development (OSX)
virtualenv -p /usr/bin/pypy .venv
source .venv/bin/activate
pip install -r requirements.txt
python post_request.py

Send a HTTP request to port 5000 from frontend

## For Production (Ubuntu 14.04 Dockerfile)
sudo docker build -t imhungry_api_img .
sudo docker run -name imhungry_api_instance \
                -p 5000:5000 \
                -e CONSUMER_SECRET='enter yelp consumer secret' \
                -e TOKEN='enter yelp token'
                -e CONSUMER_KEY='enter yelp consumer key'
                -e TOKEN_SECRET='enter yelp token secret'
                -i -t imhungry_api_img

TODO:
- Add script to handle logs for production
- Add tests
