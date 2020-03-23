FROM debian:buster

RUN apt-get update -y
RUN apt-get install -y python3 python3-pip python3-dev libpq-dev gunicorn
RUN apt-get install -y curl
RUN CHROMEDRIVER_URL=https://chromedriver.storage.googleapis.com/79.0.3945.36/chromedriver_linux64.zip \
&& CHROME_URL=https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
&& apt-get install -y libnss3-dev unzip \
&& if [ ! -x /usr/local/bin/chromedriver ]; then curl -O ${CHROMEDRIVER_URL} \
&& unzip -o chromedriver_linux64.zip \
&& mv chromedriver /usr/local/bin \
&& chmod 700 /usr/local/bin/chromedriver; fi \
&& if [ ! -x /opt/google/chrome/google-chrome ]; then curl ${CHROME_URL} -o /chrome.deb \
&& dpkg -i /chrome.deb || apt-get update -y && apt-get upgrade -y || apt --fix-broken install -y \
&& rm /chrome.deb; fi
RUN pip3 install pipenv

ARG CACHEBUST=1
WORKDIR /FbScraper
COPY . .
RUN pipenv install --system

ENV CHROMEDRIVER_BIN=/usr/local/bin/chromedriver