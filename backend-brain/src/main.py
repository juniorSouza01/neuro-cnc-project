from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import json
import paho.mqtt.publish as mqtt_pub
from src.database.db_connector import save_telemetry, get_recent_telemetry, save_action
from src.ai_core.inference import InferenceEngine
from src.ai_core.train import init_model
from src.config import Config

app = FastAPI()
ai_engine = InferenceEngine()

try:
    init_model()
    ai_engine = InferenceEngine()
except Exception as e:
    print(f"Erro init model: {e}")

class TelemetryData(BaseModel):
    timestamp: str
    spindle_load: float
    temp: float
    run_id: int = 0 

class MetrologyResult(BaseModel):
    part_id: str
    measured_deviation: float 

@app.post("/telemetry")
async def receive_telemetry(data: TelemetryData):
    save_telemetry(data.dict())
    return {"status": "ok"}

@app.post("/metrology")
async def process_metrology(result: MetrologyResult):
    print(f"CMM Report: Erro de {result.measured_deviation}mm")
    
    if abs(result.measured_deviation) < 0.005:
        return {"status": "Within tolerance"}

    recent_data = get_recent_telemetry(limit=100)
    static_context = [1.0, 55.0, 10.0] 
    
    predicted_adjustment = ai_engine.predict_adjustment(recent_data, static_context)
    
    final_adjustment = predicted_adjustment
    
    if abs(predicted_adjustment) < 0.001: 
        final_adjustment = -result.measured_deviation 

    action_id = save_action(result.part_id, final_adjustment)
    
    return {
        "processed": True, 
        "ai_suggestion": final_adjustment,
        "action_id": action_id,
        "status": "Waiting Approval"
    }

@app.post("/approve_action/{action_id}")
async def approve_action(action_id: int):
    command_payload = {
        "target_var": "VC100",
        "value": -0.007,
        "reason": "Human Approved"
    }
    
    mqtt_pub.single(
        "machine/okuma01/command",
        payload=json.dumps(command_payload),
        hostname=Config.MQTT_HOST
    )
    return {"status": "Command Sent to CNC"}