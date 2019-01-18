web: DATABASE_URL=$(heroku config:get DATABASE_URL -a protected-dawn-87362) gunicorn app:app --log-file -
worker: DATABASE_URL=$(heroku config:get DATABASE_URL -a protected-dawn-87362) python streamer.py
