# 爬虫框架AISPIDER
## 首先申明: 该框架并没有什么黑科技,只是将写爬虫脚本过程中的几个常用步骤封装了起来.比如请求, 请求异常处理, 去重, 源代码解析, 数据保存等, 主要的爬虫逻辑还是需要自行编写.

### 1.你只需要把你要请求的网址构造成框架规定的格式，然后放入到工作队列中即可， 其他的请求的相关处理， 线程池都已经封装好了。
### 2.当请求之后，若成功框架会返回请求的内容与请求的网址， 当请求由于出现异常时，会有错误日志出现。
### 3.解析部分还是按需选择吧，提供了re， lxml和 json的解析接口，但是具体的解析路径如xpath，pattern还是需要自己写的
### 4.若想保存数据，默认提供保存到mongodb中。
### 5.提供较为完善的日志文件，可以快速定位到异常。

* 脚本修改记录于\[修改记录.md\]   

* 该框架为轻型爬虫框架, 主要的工作原理就是定义两个队列,分别为任务队列与保存队列. 将请求任务放到工作队列中, 将获取的结果放入到保存队列中. 然后分别定义相应的处理函数, 来对队列中的数据进行处理.

* 采用线程池处理.

* 该框架封装的请求方法有GET和POST,.
 
* 该框架部分设计思路继承自**SCRAPY**.

* 案例脚本在framework_test文件夹中.

* 框架的配置脚本解释见config_example.py, 在具体应用时, 需要在自己的文件夹内定义一个config.py文件.

* 在此感谢姜某坤, 许某杨 不打扰之恩, 哈哈.

## 一　运行图
![运行图](http://qiniu.cuiqingcai.com/wp-content/uploads/2017/09/流程图2.png   "运行图")


- 主程序中首先**构造特定格式的带着url**放入**工作队列**,作为**root_url**, 特定格式如下:
> put_data = {
        'args': args, 
        ‘work_func': work_func,
        'follow_func': follow_func,
        'dont_filter': dont_filter,
        'need_save': need_save,
        ‘save_func': save_func,
        ‘meta’:meta
            }
            
  解析如下：

**[args]** 

 字典格式  键:url为必须 ,  diy_header为用户自定义的header, 一般需要使用特殊header时,可以使用; 还可以定义其他的相关请求参数.如下: sleep_time, time_out, retry_times, use_proxy, ua_type，ip(下面有详细解释)

**[work_func]** 

 请求函数, 必须, 一般就写成[downloader.request], 这是框架内默认的请求函数;  也可以自定义函数,但是自定义的函数必须返回请求内容 及url这两个字段内容.

**[follow_func]** 

当前数据放入队列后, 下一步的处理函数, 当tag为to_get_url的时候必须定义

**[dont _filter]** 

 不需要过滤 , 非必须, 布尔型, 默认值为False,  模拟自scrapy.

**[need_save]** 

是否需要保存 , 非必须, 布尔型, 默认为True.

**[save_func]** 

保存函数, 用户自定义.当need_save为真的时候, 必须定义这个函数. 这个函数只能有一个参数,推荐写 response.

**[meta]** 

其他想要随着请求进入下一步函数中的数据 ,非必须, 模拟自scrapy.

## 二  具体模块
#### 该框架封装了如下模块:
* 配置;
* 数据保存;
* 网页解析;
* 日志;
* 请求;
* 多线程模块;
* 工具;

### (1)config.py 
配置模块, 需要根据实际情况来配置, 该模块名不能变.
包括以下参数:

- 爬虫名称  
` spider_name = 'frame_work_test' `   
- 日志所在的文件夹名, 可自定义  
`log_folder_name = '%s_logs' % spider_name`  
`delete_existed_logs = True`  # 是否删除已有日志  

- 请求参数设置  
`thread_num = 10`  # 线程数, 保存线程为工作线程的两倍   
`sleep_time = 0.2 `# 请求休息时间   
`retry_times = 10 ` # 最大重试次数   
`timeout = 5 ` # 请求最大等待时长   

- 当use_proxy为True时，必须在请求的args中或者在配置文件中定义ip, eg: ip="120.52.72.58:80", 否则程序将报错    
`use_proxy = False`   
`ip=None`   
`ua_type = 'pc' ` # 浏览器头类型, 手机为mobile  

- 队列顺序   
` FIFO=0 ` # FIFO先进先出, LIFO 后进先出   

- 自定义浏览器头, 默认提供的浏览器头包括user_agent 和host, 若需要更丰富的header,可自行定定义新的header,并赋值给diy_header, 默认这里为None.    
`diy_header = None `     

- 定义状态码,不在其中的均视为请求错误或异常    
`status_code = [200, 304, 404]`    

- 保存设置
 
`conect = False` # 默认不连接    
`host = host`    
`port = port`     
`database_name = database_name`    

### (2) data_save
当用户需要将数据保存到MONGODB数据库中的时候,可以使用该模块.

其中定义了一个pipeline 单例对象, 默认的数据都是保存到MONGODB中, host, port, database_name都可以在配置文件中进行配置. collection_name为了使得程序更加灵活,所以要在爬虫程序中自己定义.

- 存数据的时候定义了两种模式:    
[1] 有 _id     
默认是这种模式,根据_id来进行存数据,使用update方法.    
[2] 无 _id.    
直接insert插入数据.    

- 调用:.    
`pipeline.process_item(item, collection_name, user_id=True)`.    
item 需要保存的数据,字典格式..    
当use_id为真的时候,需要在其中定义_id键, 否则会报错,默认为True..    
其中,collection_name 集合名称..    

- 当用户想保存数据到MONGODB数据库中但是又不想使用框架提供的 process_item函数的时候,也可以调用pipeline.db[mongodb客户端对象]自己写保存的方法..    

### (3) html_parser
其中定义了一个parser单例对象, 默认的有3种处理数据的方式..    

* [1] get_data_by_xpath      
调用:     
`get_data_by_xpath(html_page_source,urls_xpath))`     
html_page_source 请求返回的源代码     
urls_xpath 爬虫中定义的xpath     

* [2] get_data_by_re     
调用:      
`get_data_by_re(html_page_source,pattern))`     
html_page_source 请求返回的源代码     
pattern 爬虫中定义的pattern     

* [3] get_data_by_json     
调用:     
`get_data_by_json(html_page_source)`     
html_page_source 请求返回的源代码     

### (4) log_format
其中定义了一个logger单例对象     

* 调用:     
`spider_log(log_name=spider_name, file_folder=log_folder_name, level=logging.INFO,delete_existed_log=delete_existed_logs)`     
log_name  日志名, 取配置中的 spider_name     
file_folder  文件夹名, 取配置中的 log_folder_name     
delete_existed_log  是否删除已经存在的日志文件夹, 取配置中的 delete_existed_logs     

### (5) page_downloader
其中定义了一个aispider单例对象, 采用布隆过滤来进行过滤, 请求采用requests.get 和 requests.post方法.     

* 调用:     
`request(_args, dont_filter=False)`     

* 其中_args包括以下字段:     
url=url, sleep_time=sleep_time, timeout=timeout, retry_times=retry_times,use_proxy=use_proxy,ua_type=ua_type, diy_header=diy_header     
method=method, submit_data=submit_data

**[1] url**      
请求网址,会对网址的有效性进行检测,从队列数据中获取

**[2] dont_filter**      
不过滤  默认为False 及默认的为过滤掉,从队列数据中获取

**[3] sleep_time**      
请求休息时间, 当队列数据中未定义的时候从配置文件中获取

**[4] timeout**      
超时时长, 当队列数据中未定义的时候从配置文件中获取

**[5] retry_times**      
请求失败重试次数, 当队列数据中未定义的时候从配置文件中获取

**[6] use_proxy**      
是否使用代理, 当队列数据中未定义的时候从配置文件中获取
     
**[7] ua_type**      
请求头种类, 当队列数据中未定义的时候从配置文件中获取

**[8] diy_header**      
自定义请求头, 当队列数据中未定义的时候从配置文件中获取

**[9] ip**      
代理IP, 当队列数据中未定义的时候从配置文件中获取

**[10] method**      
请求方法,默认设置为get, 若需要定义为post, 则设置method=post即可,     

**[11] submit_data**      
submit_data, 请求过程中需要提交的数据, 当方法为post的时候, submit_data必须为字典格式, 严格按照requests库的要去, 否则会直接报错,退出程序

* 返回:

` 请求内容, 请求网址`

### (6)  threads_use_tag
* 其中定义了2个队列: **work_queue** 和**save_queue**, 有两种格式, **先进先出(FIFO)** 和 **先进后出(LIFO)**, 需要在配置文件中指明.      

* 在本模块中,将请求函数返回的网址及内容分别放入原来取出来的队列中, 键分别为**content** ,**url **. 所以在主程序中 **follow_func** or **save_func**的参数 **只有一个**,推荐写为**response**. 取数据的时候, 采用`response.get()`的方式,如获取请求内容则可以写成`response.get(‘content’)`      
 
**work_queue**      
工作队列, 所有需要处理的请求都要在主程序中构造好数据然后放入其中.当定义了save_func的时候, 请求得到的内容与请求网址将被放入数据保存队列中;
当定义了follow_func的时候,将直接执行该函数. 

**save_queue**      
数据保存队列,在save_func中进行数据的获取与保存.
 
### (7)tools.py
常用的工具函数 

##    TODOLIST
* 星期二, 12. 九月 2017 02:44下午 
` 保存爬取进度，做到可以断点续爬`# AiSpider

## 欢迎加微信 和我交流
![扫我](http://qiniu.cuiqingcai.com/wp-content/uploads/2017/09/webwxgetmsgimg.jpg  "扫我")
