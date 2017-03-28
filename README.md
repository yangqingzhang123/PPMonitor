PPMonitor
=========

访问地址: http://oa.mioji.com/ppmonitor/
目前程序运行在: 10.10.183.131:/search/fangwang/PPMonitor

项目结构
--------

1.	common: 一些通用的代码。目前包含处理数据库操作的 db\_monitor.py; 封装一些工具函数的 utils.py，目前包含时间格式化的 date\_formatter
2.	static: 包含 css, js, 字体 等静态文件。css 主要是来自 bootstrap 框架，ppmonitor.css 完成左侧导航栏的样式； js 目录中，bootstrap*.js 同样来自 bootstrap 框架，echarts.common.min.js 实现绘制图表的 [echarts](http://echarts.baidu.com/) 框架，jquery.js 是引用的 jquery 模块
3.	templates: 各个页面的模板，由于每个页面输入和展示的内容不太一致，新加接口的时候需要同时增加对应的页面
4.	conf: 各个接口统计的配置配置文件，具体规则见下面的配置文件说明
5.	PP*.py: 实现各个接口功能
6.	chart.py: 对折线图和饼图所需要数据的格式化
7.	formatter.py: 统计数据的通用处理，需要配置 conf 文件，
8.	monitor.py: 服务入口，通过 Python Tornado 框架启动服务，然后实现各个接口的路由，新加接口的时候需要在 Application 初始化的时候指定对应的路由，并绑定到对应的请求处理模块上

配置文件说明
------------

[接口代码]

-	name: 统
-	item\_list: 统计项目列表，使用竖线分隔
-	chart: 图表类型，目前只支持 LINE 或 PIE
-	y\_max: Y 轴最大值，默认为 120
-	y\_min: Y 轴最小值，默认为 0
-	label_format: TIME##|FLAG## X 轴，因为目前都是时间，所以竖线前面表示获取时间，竖线后面是获取时间字符串中的部分，## 后面跟时间格式。此处如果传给 convert_data 的 flag\_name 为 NULL 才选择 FLAG 对应的格式，如果不为 NULL 则使用 flag\_name 对应的格式。

[item1]

-	name: 统计项目的名称
-	req\_count: 统计项目数据获取的字段，如果是 LINE 则表示待统计数据的数量，数据是具体的表达式，则需要通过表达式过滤，比如 : type==csv010
-	success\_count: 成功数量的获取规则，一般都是表达式，如 : is\_success==1
-	value: 要统计的指标，分为 RATE（成功率), COUNT(成功个数)

上面的的 req\_count 和 success\_count, 格式是 VALUE/COUNT|xxx==xxx, COUNT 表示计数模式，累加符合条件的值，VALUE 表示直接取值模式，等号后面的值随便给一个即可。
