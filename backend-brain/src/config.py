import os

class Config:
    # Conexão Banco de Dados
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_NAME = os.getenv("POSTGRES_DB", "neurocnc")
    DB_USER = os.getenv("POSTGRES_USER", "postgres")
    DB_PASS = os.getenv("POSTGRES_PASSWORD", "neurocnc_secret")
    
    # Conexão MQTT
    MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
    MQTT_PORT = 1883
    
    # Configurações do Modelo
    MODEL_PATH = "src/ai_core/weights/neuro_resnet_v1.pth"
    SAFETY_LIMIT_MM = 0.05