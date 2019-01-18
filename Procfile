web: DATABASE_URL=$(heroku config:get DATABASE_URL -a your-app) gunicorn server:app
worker: DATABASE_URL=$(heroku config:get DATABASE_URL -a your-app) python streamer.py
