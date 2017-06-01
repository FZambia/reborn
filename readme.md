Reborn is a dashboard for interesting content.

See [demo gif (~70mb)](https://i.imgur.com/bjk8QQM.gifv)

![Screenshot](https://raw.githubusercontent.com/FZambia/reborn/master/screenshot.png)

It was built for my personal needs – to get content from reddit.com filtered by score. But looks like it can be used to collect content from other resources with similar mechanics too.

The idea is simple - I'll try to describe it in terms of Reddit. On Reddit there are many subreddits I am interested in. My everyday pattern is go to Reddit and check out my favorite subreddits for interesting news. With Reborn I can create subscriptions to news in subreddits that achieved a certain vote score and those news will be retrieved from Reddit API and saved into Reborn database. Saved entries can be viewed via Reborn web interface and also Reborn supports notifications to Telegram chat.

Currently Reborn optimized for personal single-user setup, though it's possible to add users via admin interface. Reborn uses SQLite as database – but as backend built on top of Django it's not a difficult task to use MySQL or PostgreSQL as more performant and scalable alternative. Also at moment Telegram notifications can be sent to one chat only (chat id must be defined in configuration file). Another caveat is that Reddit loader is built into backend, Reborn has HTTP API so it's possible to create custom decoupled loaders for other custom content providers.  

To run clone repo and create `config.json` file inside `server` directory (this `config.json` file is git-ignored):

```json
{
  "app.debug": false,
  "app.secret_key": "XXX",
  "app.database.url": "sqlite:////db/reborndb.sqlite3"
}
```

You need to have `docker` and `docker-compose` installed. If you have them installed run:

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

Open http://localhost:10000/ - it should show login screen. You now need a user account. To create user:

```
make createsuperuser
```

And then use its credentials to proceed to app. In admin interface (http://localhost:10000/admin/) you can also create new users.

SQLite database will be created inside `./data` directory - this directory is a mounted volume to container so database is persistent. Like configuration file it's git-ignored.

### Loaders

Reborn has builtin loaders for Reddit and Hacker News.

To enable Reddit loader add to config:

```json
{
    ...
    "loaders.reddit.enabled": true,
    "loaders.reddit.client_id": "XXX",
    "loaders.reddit.secret": "XXX"
}
```

– where `"loaders.reddit.client_id"` and `"loaders.reddit.secret"` are credentials of Reddit application you should create on reddit.com site. Restart service.

Create provider in admin interface with name `reddit` (http://localhost:10000/admin/core/provider/) and then start creating subscriptions on subreddits in web interface. Your subscriptions will be populated with entries very soon (by cron job inside container). 

For Hacker news create provider with name `hacker news` and add to config file:

```json
{
    ...
    "loaders.hackernews.enabled": true
}
```

Available sources are `top`, `ask`, `show`, `new`, `best` - make subscriptions on those you are interested in using web interface and set score you like to filter entries by.

You can create custom providers and loader for it. Reborn has HTTP API that allows to upload new entries for provider subscriptions. More details soon.

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

You can develop using `docker-compose` as described above (you need to restart it every time you make changes in Python code) but it uses prepared minified web app - to modify Javascript web app you need to run webpack, Django server and use Nginx.

You run Django server as usual - create virtualenv, install dependencies from `requirements.txt` and then:

Create `config.json` in `server` directory:

```json
{
    "app.debug": true
}
```

Start Django server:

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
