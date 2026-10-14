from kafka import KafkaConsumer
import json

consumer = KafkaConsumer('transactions',bootstrap_servers=['localhost:9092'],
                         value_deserializer=lambda x: json.loads(x.decode('utf-8')))

print("messages waiting from kafka...")

for message in consumer:
    message_value = message.value
    print(f"Message was come message is:    {message_value}")