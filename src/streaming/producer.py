import json
import time
from pathlib import Path
import pandas as pd
from kafka import KafkaProducer
from kafka.errors import KafkaError

# Proje kök dizinini belirleme
ROOT_DIR = Path(__file__).parent.parent
DATA_PATH = ROOT_DIR / "data" / "creditcard.csv"

def create_producer():
    """Üretim standartlarında KafkaProducer yapılandırması."""
    return KafkaProducer(
        bootstrap_servers=['localhost:9092'],
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        # Üretim Parametreleri:
        acks='all',          # Tüm broker'ların mesajı onaylamasını bekle
        retries=5,           # Hata durumunda 5 kez yeniden dene
        retry_backoff_ms=1000 # Yeniden denemeler arası 1 saniye bekle
    )

def stream_transactions():
    print("Kafka Producer başlatılıyor...")
    producer = create_producer()
    
    if not DATA_PATH.exists():
        print(f"Hata: Veri dosyası bulunamadı -> {DATA_PATH}")
        return

    df = pd.read_csv(DATA_PATH)
    print(f"Veri seti yüklendi. Toplam satır sayısı: {len(df)}")
    print("İşlem akışı (streaming) başlatılıyor...\n")

    try:
        for index, row in df.iterrows():
            transaction = row.to_dict()
            
            try:
                # Asenkron gönderme ve teslimat onayı (future)
                future = producer.send(topic='transactions', value=transaction)
                
                # Broker'dan 10 saniye içinde yanıt gelmezse zaman aşımı (timeout) tetiklenir
                record_metadata = future.get(timeout=10)
                
                print(f"[BAŞARILI] Satır {index} | Topic: {record_metadata.topic} | Partition: {record_metadata.partition} | Offset: {record_metadata.offset}")
                
            except KafkaError as ke:
                print(f"[KAFKA HATASI] Satır {index} gönderilemedi. Hata: {ke}")
                # Üretim ortamında burada başarısız mesajlar bir Dead Letter Queue (DLQ)'ya yazılabilir.
                
            except Exception as e:
                print(f"[BEKLENMEYEN HATA] Satır {index}: {e}")

            # Gerçek zamanlı akış hissi için 1 saniyelik gecikme
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nProducer kullanıcı tarafından durduruldu.")
    finally:
        producer.flush()
        producer.close()
        print("Kafka Producer güvenli bir şekilde kapatıldı.")

if __name__ == "__main__":
    stream_transactions()

#ilk olarak consumer kanalı dinlemeli sonra producer çalıştırmalı yani ilk olarak dinleme aktif edilmeli      