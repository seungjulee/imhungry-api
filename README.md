# API Server for I'm Hungry - Your Local Food Porn
http://devpost.com/software/i-m-hungry

# Warning!!
This project no longer works. Yelp noticed the crawling server and blocked it. If you want to still use it for personal purposes, try Selenium. It was built over one weekend, and didn't have time to go through thorough test.

## For Development (OSX)
```bash
1. virtualenv -p /usr/bin/pypy .venv
2. source .venv/bin/activate
3. pip install -r requirements.txt
4. python post_request.py
5. Send a HTTP request to port 5000 from frontend
```

## For Production (Ubuntu 14.04 Dockerfile)
```bash
1. sudo docker build -t imhungry_api_img .
2. sudo docker run \
				-name imhungry_api_instance \
                -p 5000:5000 \
                -e CONSUMER_SECRET='enter yelp consumer secret' \
                -e TOKEN='enter yelp token' \
                -e CONSUMER_KEY='enter yelp consumer key' \
                -e TOKEN_SECRET='enter yelp token secret' \
                -i -t imhungry_api_img
```

## TODO:
- Add script to handle logs for production
- Add tests
