# PingTrace-API
Simple api let you get ping and route info from your server to some destination.

You may adjust configuration in the program.
Originally write to cooperate with a bot to provide server info.

## Requirement
python(>=3.6.0) aiohttp <br>
Additional for traceroute: linux system package traceroute
## API-Usage:
We recommend you to run this api with screen, because it's a listener, but not a daemon itself.<br>
After the program successfully initalized, Press Ctrl+A Ctrl+D to quit. the program will continue running.<br>
While the program is running, access http://yourIP:yourport/key/?apitype&parameter1=xxx&parameter2=xxx to use its api.<br><br>
### Parameter Explain
#### yourport:
which you selected listen port,default is 4096.when both ipv4 and ipv6 available,it will listen at both ipv4 and ipv6.<br>
#### key:
your api key.<br>
#### apitype:
available value<br>
{pingapi,traceapi,traceapi_fast,traceapi_v6,traceapi_v6_fast}<br>
##### pingapi:
a tcp ping tool.when received the request,the api will tcping with both ipv4 and ipv6,then return both ipv4 and ipv6 latency.essential parameter:ip,port<br>
##### traceapi:
a traceroute tool.when received the request,the api will traceroute to target,then return the result (include the location display).essential parameter:ip<br>
##### traceapi_v6:
the same as traceapi,but force ipv6.<br>
##### traceapi_fast:
the same as traceapi,but no location searching(will not handed any ip to IP to location api)<br>

## Note

This api's default language is zh_CN,you can modify the location display code to let it showing what you want.<br>
Default IP format is 123:45:67:89,because like the xxx.xxx.xxx.xxx will be shown in blue and underline in QQ,so we force it shows with ":" instead "."<br>

# 简体中文说明

本API可以通过非常简单的方式来让你通过你的服务器来测试一些网络情况。

你可以任意调整该程序的参数，其中KEY是必须调整的。

## 依赖
python(>=3.6.0) aiohttp<br>
traceroute 额外依赖: linux 系统包 traceroute
## API用法:
我们强烈推荐您使用screen，在screen里执行。本程序没有自我保活功能。待Init完毕之后，按Ctrl+A Ctrl+D退出，此时API仍然会正常继续运行。<br>
当程序正常运行并且对应的端口防火墙已经开放时，访问http://你的IP地址:你设定的端口号/api密钥（KEY）/?api类型&参数1=xxx&参数2=xxx<br><br>
### 参数解释
#### 你设定的端口号:
该端口号指的是你将在你的IP地址的哪个端口运行该API，默认值是4096.当IPV6可用时，程序将会同时监听IPV4与IPV6。<br>
#### api密钥（key）:
你的API密钥，此字段为了防止未授权的用户擅自操作API所用。<br>
#### api类型:
合法的API类型值<br>
{pingapi,traceapi,traceapi_fast,traceapi_v6,traceapi_v6_fast}<br>
##### pingapi:
该参数代表着将使用一个tcping请求，当接收到参数ip和port端口时，程序将通过内部函数对目标服务器和端口进行一次tcping，若IPV6可用，则同时返回IPV4与IPV6的延迟值，若只有IPV4可用，则只返回IPV4。必要参数：ip，port<br>
##### traceapi:
该参数代表将使用一个路由追踪请求，当接受到参数ip时，程序将通过内部函数对目标服务器进行traceroute，并在数秒后返回路由追踪数据，包含每一跳的路由物理位置信息。必要参数：ip<br>
##### traceapi_v6:
与traceapi相同，但强制IPV6路由追踪。<br>
##### traceapi_fast:
与traceapi相同，但不查询每一跳的ip物理地址信息。<br>

## 注意

本API的默认语言是简体中文，您可用自行修改地址信息的接口让它显示任何您所需要的API信息。<br>
默认输出的路由追踪IP与主机名的"."均被替换为":"，因为该API利用于QQ机器人时，会输出大量难看的蓝色下划线影响阅读，所以我们强制使用":"<br>

