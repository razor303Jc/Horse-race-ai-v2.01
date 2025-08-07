"""Configuration for Horse Racing AI v2.0"""

import os

class Config:
    SECRET_KEY = 'horse-racing-ai-v2-secret-key'
    DEBUG = True

class DevelopmentConfig(Config):
    pass

def get_config(environment='development'):
    return DevelopmentConfig
