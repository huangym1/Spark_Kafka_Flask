from kafka import KafkaProducer
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
from pyspark import SparkConf, SparkContext
import json
import sys

def KafkaWordCount(zkQuorum, group, topics, numThreads):
    spark_conf = SparkConf().setAppName("KafkaWordCount").set('spark.io.compression.codec','snappy')
    sc = SparkContext(conf=spark_conf)
    sc.setLogLevel("ERROR")
    ssc = StreamingContext(sc, 1)
    # 这里表示把检查点文件写入分布式文件系统HDFS，所以要启动Hadoop
    ssc.checkpoint(".")
    topicAry = topics.split(",")
    # 将topic转换为hashmap形式，而python中字典就是一种hashmap
    topicMap = {}
    for topic in topicAry:
        topicMap[topic] = numThreads

    # 从kafka中创建一个input stream，类型是TransformedDStream
    lines = KafkaUtils.createStream(ssc, zkQuorum, group, topicMap).map(lambda x: x[1]) # (None, 'x')
    words = lines.flatMap(lambda x: x.split(" "))
    # reduceByKeyAndWindow _+_是对新产生的时间分片（time4,time5内RDD）进行统计，而_-_是对上一个窗口中，过时的时间分片进行统计
    wordcount = words.map(lambda x: (x, 1)).reduceByKeyAndWindow((lambda x, y: x + y), (lambda x, y: x - y), 1, 1, 1)
    # wordcount的值像('1',3)('0',4)，这里所有tuple组成的数据就是rdd
    wordcount.foreachRDD(lambda x: sendmsg(x))
    ssc.start()
    ssc.awaitTermination()

# 格式转化，将[('1', 3), ('0', 4), ('2', 3)]变为[{"1": 3}, {"0": 4}, {"2": 3}]
def Get_dic(rdd_list):
    res = []
    for elm in rdd_list:
        tmp = {elm[0]: elm[1]}
        res.append(tmp)
    # 列表/字典 --> 字符串
    return json.dumps(res)

def sendmsg(rdd):
    if rdd.count != 0:
        msg = Get_dic(rdd.collect())
        # 实例化一个KafkaProducer示例，用于向Kafka投递消息
        producer = KafkaProducer(bootstrap_servers='localhost:9092')
        producer.send("result", msg.encode('utf8')) # msg是字符串，如[{"1": 3}, {"0": 4}, {"2": 3}]
        # 很重要，不然不会更新
        producer.flush()


if __name__ == '__main__':
    # 输入的四个参数分别代表着
    # 1.zkQuorum为zookeeper地址
    # 2.group为消费者所在的组
    # 3.topics该消费者所消费的topics
    # 4.numThreads开启消费topic线程的个数
    if (len(sys.argv) < 5):
        print("Usage: KafkaWordCount <zkQuorum> <group> <topics> <numThreads>")
        exit(1)
    zkQuorum = sys.argv[1]
    group = sys.argv[2]
    topics = sys.argv[3]
    numThreads = int(sys.argv[4])
    print(group, topics)
    KafkaWordCount(zkQuorum, group, topics, numThreads)
