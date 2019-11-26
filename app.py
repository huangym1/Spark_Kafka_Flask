import json
from flask import Flask, render_template
from flask_socketio import SocketIO
from kafka import KafkaConsumer

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
thread = None
# 实例化一个consumer，接收topic为result的消息
consumer = KafkaConsumer('result')

# 一个后台线程，持续接收Kafka消息，并发送给客户端浏览器
def background_thread():
    girl = 0
    boy = 0
    for msg in consumer:
        data_json = msg.value.decode('utf8')
        data_list = json.loads(data_json)
        for data in data_list:
            if '0' in data.keys():
                girl = data['0']
            elif '1' in data.keys():
                boy = data['1']
            else:
                continue
        result = str(girl) + ',' + str(boy)
        print(result)
        socketio.emit('test_message',{'data':result})

# 客户端发送connect事件时的处理函数，服务端收到客户端发过来的action为'test_connect'，就开始执行下面内容
@socketio.on('test_connect')
def cn(message):
    print(message)
    global thread
    if thread is None:
        # 如果线程不存在，开启线程发送数据到客户端
        thread = socketio.start_background_task(target=background_thread)
    socketio.emit('connected', {'data': 'Connected'})

@app.route("/")
def handle_mes():
    return render_template("index.html")

if __name__ == '__main__':
    # debug运行
    socketio.run(app,debug=True,host="0.0.0.0")