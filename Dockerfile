FROM python:3.6

# Ensure that Python outputs everything that's printed inside
# the application rather than buffering it.
ENV PYTHONUNBUFFERED 1

# We need cron to periodically execute management command to 
# load content from providers.
RUN apt-get update && apt-get install -y cron

ADD ./deploy/crond/ /etc/cron.d/

RUN chmod +x /etc/cron.d/reborn

RUN mkdir /server

WORKDIR /server

ADD ./server/requirements.txt /server/

RUN pip install -r requirements.txt

ADD ./server /server/

RUN mkdir /db

VOLUME /db

RUN /server/manage.py collectstatic --noinput

VOLUME /static

CMD /etc/init.d/cron start && uwsgi --ini uwsgi.ini
