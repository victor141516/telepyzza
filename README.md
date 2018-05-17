# Telepyzza


> «el secreto está en el docker»


## What is `telepyzza`?

`telepyzza` is a dockerized python telegram bot thats run docker containers for each user and bring to them a python interpreter. more or less. aprox.

and pip.

and confusion.


# Install

1. Get a bot token talking to @BotFather
2. Install Docker
3. Run:
   - You can use docker-compose, but it may not work for you. You can find a `docker-compose.yml` but I will continue assuming you
   - use Docker `a pelo` like follows:

	 ```
	 $ git clone https://github.com/victor141516/telepyzza.git
	 $ docker build –t docker_papi telepyzza
	 $ docker network create telepyzza
	 $ docker run -d --rm --name docker_papi \
		    --network telepyzza \
		    -e TG_TOKEN=YOUR_TOKEN_HERE \
		    -e DOCKER_NETWORK=telepyzza \  # This MUST be the same as the network name
		    -e WEBHOOK_URL=https://yourdomain.tld \ # You can uset this variable and the bot will work in polling mode
		    -v /var/run/docker.sock:/var/run/docker.sock \
		    -w /app docker_papi gunicorn -w1 -b :8000 docker_papi:app
	 ```

Now you have the bot running in your Docker, but it can't be connected through internet, so you can use polling (_**boring**_, not recommended) or you can

# Use Caddy
Caddy will allow you to expose your bot to the terrifing internet. You have to own a domain, if it's not your case you can always use polling (just remove `-e WEBHOOK_URL=`... from the last command).

Now that you have your shiny fabulous domain, let's say it's `telecosas.bot`, you can use Caddy as reverse proxy to expose your bot.

## PASOS
###### ↖ "Steps"
I won't focus on using Caddy as this is not the purpose of this README.md but here we go:

1. Hardest thing first: Caddyfile. This is the config file for Caddy. Mine looks like this:

	```
	telepy.telecosas.bot {
		proxy / docker_papi:8000 {
		    header_upstream Host {host}
		    header_upstream X-Real-IP {remote}
		    header_upstream X-Forwarded-Proto {scheme}
		}
		gzip
	}
	```
	Yours may vary. For example, my domain has a wildcard subdomain and I can use any subdomain I want. You will have to check Caddy documentation to know how you can write your Caddyfile. I won't link Caddy documentation, you are old enough to Google it. I know it would take me less time linking it than writting this. Shut up.

2. Once you have your Caddyfile, it comes the easy part: run a Caddy container (_yayyyy_):

	```
	$ docker run -d --rm --network caddywork \
	    -v /path/to/your/Caddyfile:/etc/Caddyfile \
	    --name caddy -p 80:80 -p 443:443 abiosoft/caddy
	```

Note the network name is different than the previous network, "why?" will you ask: because we don't want bot users be able to connect to any other container than _papi_. So you can use the same network if you want, but I suggest using a different one. If so, you will have to connect _papi_ to the new network too:

	`$ docker network connect caddywork docker_papi`


Now everything is ready, just open Chrome and type the address of your bot, it will give you a `!` if it's working.
