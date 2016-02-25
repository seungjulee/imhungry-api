# for dev OSX
virtualenv venv
venv/bin/pip install -r requirements.txt
venv/bin/python2.7 post_request.py

# for production (Ubuntu 14.04) with pypy
sudo apt-get update
sudo apt-get install -y build-essential
sudo apt-get install -y python-virtualenv
sudo apt-get install -y pypy
sudo apt-get install -y libxml2-dev libxslt1-dev python-dev
virtualenv -p /usr/bin/pypy venv
sudo venv/bin/pip install -r requirement_prod.txt
sudo venv/bin/python2.7 post_request.py

