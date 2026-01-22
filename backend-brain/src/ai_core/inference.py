import torch
import numpy as np
from src.ai_core.model import NeuroCNCModel
from src.config import Config
import os

class InferenceEngine:
    def __init__(self):
        self.model = NeuroCNCModel(num_sensors=2, static_features=3)
        self.device = torch.device("cpu") # Força CPU para evitar erro de driver no docker sem GPU
        
        if os.path.exists(Config.MODEL_PATH):
            try:
                self.model.load_state_dict(torch.load(Config.MODEL_PATH, map_location=self.device))
                print("Pesos carregados.")
            except:
                print("Erro ao carregar pesos. Usando aleatórios.")
        else:
            print("Arquivo de pesos não encontrado. Usando aleatórios.")
        
        self.model.to(self.device)
        self.model.eval()

    def predict_adjustment(self, telemetry_data, static_data):
        if not telemetry_data:
            print("Sem telemetria recente. Retornando 0.")
            return 0.0

        # Extração de features
        loads = [d['spindle_load'] for d in telemetry_data]
        temps = [d['spindle_temp'] for d in telemetry_data]
        
        # Garante tamanho fixo (Padding ou Truncate) - Janela de 100
        target_len = 100
        current_len = len(loads)
        
        if current_len < target_len:
            loads += [0] * (target_len - current_len)
            temps += [0] * (target_len - current_len)
        else:
            loads = loads[:target_len]
            temps = temps[:target_len]

        # Monta Tensor: [Batch=1, Channels=2, Time=100]
        tensor_input = torch.tensor([loads, temps], dtype=torch.float32).unsqueeze(0)
        tensor_static = torch.tensor([static_data], dtype=torch.float32)

        with torch.no_grad():
            prediction = self.model(tensor_input, tensor_static)
            
        return prediction.item()