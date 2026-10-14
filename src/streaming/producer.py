from kafka import KafkaProducer
import time
import json 
import pandas as pd

producer = KafkaProducer(bootstrap_servers=['localhost:9092'],value_serializer=lambda v: json.dumps(v).encode('utf-8') )

#data_loading


df = pd.read_csv('data/creditcard.csv')

#data sending to kafka topic

for index , row in df.iterrows():
    transaction = row.to_dict()
    producer.send(topic='transactions',value=transaction)
    print(f'Data is sending kafka "Transactions" topic data which is sent {index}')
    time.sleep(1)

#ilk olarak consumer kanalı dinlemeli sonra producer çalıştırmalı yani ilk olarak dinleme aktif edilmeli      