#!/bin/bash

cd /home/yeehchan/dev/scrapy
source /home/yeehchan/dev/scrapy/venv/bin/activate
cd /home/yeehchan/dev/scrapy/iproperty/iproperty/
scrapy crawl iproperty &> results/log_$(date +\%Y\%m\%d).txt

