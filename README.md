# hackernewsalerts-backend

The backend services for [hackernewsalerts.com](https://hackernewsalerts.com). A web application that sends email notifications when someone replies to one of your comments or posts on Hacker News.

## Architecture

I run 2 Python Django services:

- A [Django Ninja](https://github.com/vitalik/django-ninja) REST API that handles email signups - see [views.py](./alerts/views.py)
- A [Django Q2](https://django-q2.readthedocs.io/en/master/) scheduled worker that checks for updates
  and sends emails when necessary - see [tasks.py](./alerts/tasks.py)

Both services use the same Postgres database backend, and are deployed with [CapRover](https://caprover.com/) - see the `captain-definition` JSON files.

## Commands

See [Makefile](./Makefile)

## TODO

- `ALLOWED_HOSTS` and `CORS_ALLOWED_ORIGINS` in prod should only allow for frontend prod

## Notes

The scheduled worker sends email alerts to the admin user every time there's a failure. I sometimes get these alerts because of
missing data, but the data usually becomes available after a couple of hours.
