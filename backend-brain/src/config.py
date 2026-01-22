import os

class Config:
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_NAME = "neurocnc"
    DB_USER = "postgres"
    DB_PASS = os.getenv("POSTGRES_PASSWORD", "neurocnc_secret")
    MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
    MODEL_PATH = "src/ai_core/weights/neuro_resnet_150.pth"
    # Janela de tempo: Últimos 100 pontos (10 segundos a 10Hz)
    WINDOW_SIZE = 100 
    NUM_SENSORS = 5