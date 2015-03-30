# ohmyrepo
该项目利用了github的webhook功能，自动获取用户的repo的star信息，关注人的分布以及关注者的被follow的数量排名， 这样你可以选择直接follow他们。

================

## 开始安装
- `pip install -r requirement.txt`
- 进入此网址 [this url](https://github.com/settings/applications)， 添加你的一个github应用，并且设置好CLIENT_ID, CLIENT_SECRET REDIRECT_URL and ACCESS_TOKEN_URL.
- 根据之前的设置，检查并修改此文件 `settings.py` 中的对应设置。注意: `WEBHOOK_URL` 这个设置在应用成功部署后，会显示在需要记录的项目中的设置里面，如图:
![web_hook](https://raw.githubusercontent.com/no13bus/ohmyrepo/master/screen/1.png)
- 执行命令 `python app.py`, 打开网址 `http://127.0.0.1:8888` 可以看到效果。（强烈建议部署到线上环境，因为如果将webhook_url设置为本地地址的话，无法实现github的自动推送项目事件的功能）
- 假如你需要部署的话，推荐这个搭配：supervisor + nginx, 这里是具体[细节](http://www.tornadoweb.org/en/stable/guide/running.html?highlight=deploy)

## 用到的技术
- [Webhook](https://developer.github.com/v3/orgs/hooks/)
- [Tornado](https://github.com/tornadoweb/tornado)
- [Highchart](http://www.highcharts.com/)
- [mongo]()
- [redis]()

## Demo website
http://ohmyrepo.ml/show?u=no13bus&r=ohmyrepo

## 主页(github登录)
http://ohmyrepo.ml

## 项目细节
- 首先，你需要使用github账户登录网站，ohmyrepo需要你的权限包括: follow read, follow write, webhook read, webhook write.
- 然后你在 [ohmyrepo.ml](http://ohmyrepo.ml) 添加你的github的项目地址, 我们会将该项目的webhook_url设置为 `http://ohmyrepo.ml/webhook`, 然后初始化数据库，爬取该项目以前的star记录.
- 最后，如果有人之后star了你的项目，利用github的webhook功能，它会自动推送给我们star的详细信息，然后我们将其记录到数据库中。
- 你可以在README.md里面添加 `[![repo](http://ohmyrepo.ml/static/ohmyrepo.png)](http://ohmyrepo.ml/show?u=no13bus&r=redispapa)` 这样的字串，直接点击可以看到显示效果。显示效果: [![repo](http://ohmyrepo.ml/static/ohmyrepo.png)](http://ohmyrepo.ml/show?u=no13bus&r=redispapa)
- 我们使用 [motor](https://github.com/mongodb/motor) 作为 mongodb 的 tornado 异步客户端.
- 我们使用redis 作为 tornado 的缓存. 多谢 [cloverstd's](https://github.com/cloverstd) 的[项目](https://gist.github.com/cloverstd/10712505).

## 截图
![2](https://raw.githubusercontent.com/no13bus/ohmyrepo/master/screen/2.png)
![3](https://raw.githubusercontent.com/no13bus/ohmyrepo/master/screen/3.png)
![4](https://raw.githubusercontent.com/no13bus/ohmyrepo/master/screen/4.png)
![5](https://raw.githubusercontent.com/no13bus/ohmyrepo/master/screen/5.png)
![6](https://raw.githubusercontent.com/no13bus/ohmyrepo/master/screen/6.png)
![7](https://raw.githubusercontent.com/no13bus/ohmyrepo/master/screen/7.png)
![8](https://raw.githubusercontent.com/no13bus/ohmyrepo/master/screen/8.png)

## Version 0.0.1
使用highchart显示用户的repo的star的人的分布，每天的star数量的变化趋势以及被follow人数最多的top5，直接直接follow对方的功能。

## Q & A
#### 我的项目star超多，为什么网站上显示的我的项目的star记录不全呢?
因为根据 github 种关于分页数据的[说明](https://developer.github.com/v3/#pagination), 我们能获取到的历史数据只是限于几页，github为了更多人使用数据服务，限制了数据量. 当然如果你开始是没有star的话，以后的记录都会插入到网站数据库内，这样记录就会是全的。
#### 为什么我的项目的follower的世界地图分布数量之和和我的star数相差很多呢?
因为有些人的个人资料设置里面根本没有设置location，也有一些人用的是非英文，还有使用的是城市的外号，比如：帝都，寨都，魔都等等。我们目前使用的根据名字猜测具体城市名的库是 getnames.org, 但是还没有特别准确，并且有请求限制。如果你有什么好的库的话，请联系我(no13bus@gmail.com). 多谢。
