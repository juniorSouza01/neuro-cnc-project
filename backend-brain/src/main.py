from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from typing import List
import json
import paho.mqtt.publish as mqtt_pub
from src.database.db_connector import save_telemetry, get_recent_telemetry
from src.ai_core.inference import InferenceEngine
from src.config import Config

app = FastAPI(title="NeuroCNC Brain API")
ai_engine = InferenceEngine()

# Modelos de Dados (DTOs)
class TelemetryData(BaseModel):
    timestamp: str
    spindle_load: float
    temp: float

class MetrologyResult(BaseModel):
    part_id: str
    measured_deviation: float # Ex: +0.015
    
@app.post("/telemetry")
async def receive_telemetry(data: TelemetryData):
    """Recebe dados da máquina a cada 100ms"""
    save_telemetry(data.dict())
    return {"status": "ok"}

@app.post("/metrology")
async def process_metrology(result: MetrologyResult):
    """
    Recebe o resultado da CMM.
    Isso dispara o cálculo da correção para a PRÓXIMA peça.
    """
    print(f"Recebido resultado da CMM: Erro de {result.measured_deviation}mm")
    
    # 1. Buscar histórico recente da máquina (Estado)
    recent_data = get_recent_telemetry(limit=100)
    
    # 2. Dados estáticos (Mockados por enquanto)
    static_context = [1.0, 55.0, 10.0] # [Material=1, Tool=55, Dim=10]
    
    # 3. Perguntar à IA qual o ajuste
    suggested_offset = ai_engine.predict_adjustment(recent_data, static_context)
    
    print(f"IA Sugere ajuste de: {suggested_offset:.4f}mm")
    
    # 4. Enviar comando para a máquina via MQTT
    command_payload = {
        "target_var": "VC100",
        "value": suggested_offset,
        "reason": "Correction based on CMM feedback"
    }
    
    mqtt_pub.single(
        "machine/okuma01/command",
        payload=json.dumps(command_payload),
        hostname=Config.MQTT_HOST
    )
    
    return {
        "processed": True, 
        "ai_suggestion": suggested_offset
    }