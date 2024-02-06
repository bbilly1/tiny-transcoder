#!/bin/bash
# application entry script

if [ -z "$TT_PORT" ]; then
  CUSTOM_PORT=8000
else
  CUSTOM_PORT=$TT_PORT
fi

uwsgi --ini uwsgi.ini --http :$CUSTOM_PORT
