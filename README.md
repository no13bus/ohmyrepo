# ohmyrepo
use webhook to analysis automaticly that who stared your repository, where are they. Besides you can fellow some users. 

================

[中文文档](https://github.com/no13bus/ohmyrepo/blob/master/README_CN.md)

## Let's start
- `pip install -r requirement.txt`
- enter into [this url](https://github.com/settings/applications) and make your own application, then get the CLIENT_ID, CLIENT_SECRET REDIRECT_URL and ACCESS_TOKEN_URL.
- check out the file `settings.py` and make your own configure. Attention: `WEBHOOK_URL` will be used to record some repository. After this project work well, you can see it in the repository settings.
![web_hook](https://raw.githubusercontent.com/no13bus/ohmyrepo/master/screen/1.png)
- type this command `python app.py`, then you can watch it in `http://127.0.0.1:8888`
- If you deloy it, we recommand you use supervisor, nginx, this is the [details](http://www.tornadoweb.org/en/stable/guide/running.html?highlight=deploy)

## The tech we use
- [Webhook](https://developer.github.com/v3/orgs/hooks/)
- [Tornado](https://github.com/tornadoweb/tornado)
- [Highchart](http://www.highcharts.com/)

## Demo website
http://ohmyrepo.ml

## Project Details
- If you want to record your repository, you should login with github firstly. We need your authorization include repo's webhook reading and writing and user's following.
- Secondly, you add your repository in the [ohmyrepo.ml](http://ohmyrepo.ml), we set your repo's webhook payload url to ours and we initialize by recode history event.
- Thirdly, once someone star your repo, github webhook immediately post an event to our server and we insert it to database.
- You can add this string `[![repo](http://ohmyrepo.ml/static/ohmyrepo.png)](http://ohmyrepo.ml/show?u=no13bus&r=redispapa)` into your README.md file。For example: [![repo](http://ohmyrepo.ml/static/ohmyrepo.png)](http://ohmyrepo.ml/show?u=no13bus&r=redispapa)
- We use mongodb to store user and repo information. The mongodb is awesome, especially its query statement. And we use [motor](https://github.com/mongodb/motor) as tornado's mongo asynchronous client.
- We use redis as tornado cache. Thanks for [cloverstd's](https://github.com/cloverstd) good cache [library](https://gist.github.com/cloverstd/10712505).


## Project Screen
![2](https://raw.githubusercontent.com/no13bus/ohmyrepo/master/screen/2.png)
![3](https://raw.githubusercontent.com/no13bus/ohmyrepo/master/screen/3.png)
![4](https://raw.githubusercontent.com/no13bus/ohmyrepo/master/screen/4.png)
![5](https://raw.githubusercontent.com/no13bus/ohmyrepo/master/screen/5.png)
![6](https://raw.githubusercontent.com/no13bus/ohmyrepo/master/screen/6.png)
![7](https://raw.githubusercontent.com/no13bus/ohmyrepo/master/screen/7.png)
![8](https://raw.githubusercontent.com/no13bus/ohmyrepo/master/screen/8.png)


## Version 0.0.1
show users' repo star, follower infomations in the human style.

## Q & A
#### Why my repository's star recode is not as enough as it should be?
Because when initialize the repository, we can only get small amount pages history of event records by github api. As the github api said, in order to keep the API fast for everyone, pagination is limited for this resource.
#### Why my repository's followers distribution is not equal to the stars amount?
Some body do not set their location, besides we use geonames.org api to judge accurate name of your city. If you name it by nickname, take for example, you named Beijing of China to DiDU(帝都), we can not recognize it. We set the location to none. If you have better api than getnames.org, contact me(no13bus@gmail.com). Thanks.

