import torch
import os
from src.ai_core.model import NeuroCNCModel

def init_model():
    
    weights_dir = "src/ai_core/weights"
    os.makedirs(weights_dir, exist_ok=True)
    path = f"{weights_dir}/neuro_resnet_v1.pth"
    
    print("Inicializando modelo virgem...")
    model = NeuroCNCModel(num_sensors=2, static_features=3)
    
    # Salva o estado inicial (pesos aleatórios, mas válidos)
    torch.save(model.state_dict(), path)
    print(f"Modelo salvo em: {path}")

if __name__ == "__main__":
    init_model()