import multiprocessing
import os

bind = "0.0.0.0:8080"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'gevent'
worker_connections=1000
max_requests = 10000
max_requests_jitter = 1400
timeout = 0
loglevel = 'ERROR'