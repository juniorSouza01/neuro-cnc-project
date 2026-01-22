import torch
import numpy as np
from src.ai_core.model_50layers import NeuroCNCModel # Importa a classe que criamos antes
from src.config import Config
import os

class InferenceEngine:
    def __init__(self):
        self.model = NeuroCNCModel()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Carregar pesos se existirem
        if os.path.exists(Config.MODEL_PATH):
            self.model.load_state_dict(torch.load(Config.MODEL_PATH, map_location=self.device))
            print("Pesos do modelo carregados com sucesso.")
        else:
            print("AVISO: Usando modelo não treinado (pesos aleatórios).")
        
        self.model.to(self.device)
        self.model.eval()

    def predict_adjustment(self, telemetry_data, static_data):
        """
        telemetry_data: Lista de dicts dos últimos sensores
        static_data: Lista [MaterialID, ToolID, TargetDim]
        """
        # 1. Preprocessamento: Converter lista para Tensor [Batch, Channel, Time]
        # Simplificação: Pegando apenas SpindleLoad e Temp
        loads = [x['spindle_load'] for x in telemetry_data]
        temps = [x['spindle_temp'] for x in telemetry_data]
        
        # Padding se faltar dados (garantir tamanho fixo)
        # Assumindo janela de 100 pontos
        tensor_input = torch.tensor([loads, temps], dtype=torch.float32).unsqueeze(0) 
        tensor_static = torch.tensor([static_data], dtype=torch.float32)

        # 2. Inferência
        with torch.no_grad():
            tensor_input = tensor_input.to(self.device)
            tensor_static = tensor_static.to(self.device)
            
            prediction = self.model(tensor_input, tensor_static)
            
        return prediction.item() # Retorna float (mm)