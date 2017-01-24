_author="niyoufa"

import os
import sys

PROJECT_PATH = os.path.dirname(os.path.dirname(__file__))
sys.path.append(PROJECT_PATH)

# MongoDB Config
DB_HOST = 'localhost'
DB_PORT = 27017
DB_NAME = 'test'
DB_USER = ''
DB_PWD = ''

# Redis Config
REDIS_HOST = 'localhost'
REDIS_PORT = 6379

