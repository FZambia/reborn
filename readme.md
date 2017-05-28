Reborn is a dashboard for interesting content.

See [demo gif (~70mb)](https://i.imgur.com/bjk8QQM.gifv)

![Screenshot](https://raw.githubusercontent.com/FZambia/reborn/master/screenshot.png)

It was built for my personal needs – to get content from reddit.com filtered by score. But looks like it can be used to collect content from other resources with similar mechanics too.

The idea is simple - I'll try to describe it in terms of Reddit. On Reddit there are many subreddits I am interested in. My everyday pattern is go to Reddit and check out my favorite subreddits for interesting news. With Reborn I can create subscriptions to news in subreddits that achieved a certain vote score and those news will be retrieved from Reddit API and saved into Reborn database. Saved entries can be viewed via Reborn web interface and also Reborn supports notifications to Telegram chat.

Currently Reborn optimized for personal single-user setup, though it's possible to add users via admin interface. Reborn uses SQLite as database – but as backend built on top of Django it's not a difficult task to use MySQL or PostgreSQL as more performant and scalable alternative. Also at moment Telegram notifications can be sent to one chat only (chat id must be defined in configuration file). Another caveat is that Reddit loader is built into backend, Reborn has HTTP API so it's possible to create custom decoupled loaders for other custom content providers.  

To run with default behaviour which supposed to work with Reddit create `server/config.json` file:

```json
{
  "app.debug": false,
  "app.secret_key": "XXX",
  "app.database.url": "sqlite:////db/reborndb.sqlite3",
  "loaders.reddit.enabled": true,
  "loaders.reddit.client_id": "XXX",
  "loaders.reddit.secret": "XXX"
}
```

– where `"loaders.reddit.client_id"` and `"loaders.reddit.secret"` are credentials of Reddit application you should create.

And then run:

```
make up
```

After first run you need to run database migrations:

```
make migrate
```

To stop service:

```
make stop
```

You need to have `docker` and `docker-compose` installed.

Open http://localhost:10000/ - it should show login screen.

### Initial setup

Then create user:

```
make createsuperuser
```

And use its credentials to proceed to app.

Create `reddit` provider in admin interface: http://localhost:10000/admin/ and start creating subscriptions in web interface. It will be populated with entries very soon (with cron job inside container). In admin interface you can also create new users.

SQLite database will be created inside `./data` directory - this dir is mounted volume to container so database is persistent. It's git-ignored.

### Telegram notifications

To enable Telegram notifications create bot using `FatherBot`, start talking to it and get chat ID using this command:

```
curl -i -X GET https://api.telegram.org/bot<BOT_TOKEN>/getUpdates
```

Then add lines to configuration file and restart service:

```json
{
  ...
  "notifications.telegram.bot_token": "BOT_TOKEN",
  "notifications.telegram.chat_id": "CHAT_ID"
}
```

### Development

Currently it's not very comfortable - you need to run webpack, Django server and use Nginx.

You run Django server as usual - create virtualenv, install dependencies from `requirements.txt` and then:

Create `config.json` in `server` directory with `"app.debug": true` option.

```
python manage.py runserver 8000
```

To run webpack go to `web` folder and run:

```
npm run dev
```

It will create web app files in `build` directory.

And finally run Nginx that will proxy requests to Django or single-page app:

```nginx
server {
    listen 9000;
    server_name _;
    root /path/to/app/build/;

    location / {
        expires off;
        try_files $uri /index.html;
    }

    location @rewrites {
        rewrite ^(.+)$ /index.html last;
    }

    location ~ ^/(api|admin)/ {
       proxy_set_header X-Real-IP $remote_addr;
       proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       proxy_set_header Host $http_host;
       proxy_pass http://127.0.0.1:8000;
    }
}
```
