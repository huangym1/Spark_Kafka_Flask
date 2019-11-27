# spark+kafka+flume构建实时分析Dashboard
## 实现流程
1. 应用程序将购物日志发送给Kafka，topic为”sex”，因为这里只是统计购物男女生人数，所以只需要发送购物日志中性别属性即可。这里采用模拟的方式发送购物日志，即读取购物日志数据，每间隔相同的时间发送给Kafka。
2. 接着利用Spark Streaming从Kafka主题”sex”读取并处理消息。这里按滑动窗口的大小按顺序读取数据，例如可以按每5秒作为窗口大小读取一次数据，然后再处理数据。
3. Spark将处理后的数据发送给Kafka，topic为”result”。
4. 然后利用Flask搭建一个web应用程序，接收Kafka主题为”result”的消息。
5. 利用Flask-SocketIO将数据实时推送给客户端。
6. 客户端浏览器利用js框架socketio实时接收数据，然后利用js可视化库hightlights.js库动态展示。
## 运行
### 1、运行kafka_test.py
接受sex这个topic的数据，统计数据后并把结果投递到result这个topic
```
spark-submit --master spark://wong-1:7077  --executor-memory 512M --jars /usr/local/spark/jars/spark-streaming-kafka-0-8-assembly_2.11-2.4.4.jar kafka_test.py 127.0.0.1:2181 1 sex 1
```
### 2、运行producer.py
读log_result.csv这个文件，并把内容投递到sex
```
python producer.py
```
### 3、运行consumer.py
接受result的结果，并显示在终端
```
python consumer.py
```
### 4、运行app.py
启动flask，将结果展示到浏览器
```
python app.py
```
## 结果展示
![image](https://github.com/huangym1/spark_kafka/blob/master/images/chart.png)
