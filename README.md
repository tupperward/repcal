# repcalRSS
A Flask App that generates a robust RSS feed for the French Republican Calendar

The docker container is public at tupperward/repcalrss and can be run with one easy line 

`docker run -p 80:8080 -e DOMAIN=<your domain name> tupperward/repcalrss`

DOMAIN is not needed, but if left blank will only provide localhost as the origin for your images in the feed.

This was a fun project, I'm likely going to add a frontend that generates something from the most recent entry in the xml just so it's a bit prettier. Other than that, I think I'm gonna let this sorta just chill out. Reach out if you want any help with anything.
