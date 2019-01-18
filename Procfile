web: DATABASE_URL=$(heroku config:get DATABASE_URL -a your-app) gunicorn app:app --log-file -
worker: DATABASE_URL=$(heroku config:get DATABASE_URL -a your-app) python streamer.py
