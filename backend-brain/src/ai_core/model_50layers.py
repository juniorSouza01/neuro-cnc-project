import torch
import torch.nn as nn

class ResidualBlock(nn.Module):
    """Um bloco residual contendo 2 camadas de convolução.
    Usaremos 16 destes blocos = 32 camadas."""
    def __init__(self, channels):
        super(ResidualBlock, self).__init__()
        self.conv1 = nn.Conv1d(channels, channels, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm1d(channels)
        self.relu = nn.ReLU()
        self.conv2 = nn.Conv1d(channels, channels, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm1d(channels)

    def forward(self, x):
        residual = x
        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)
        out = self.conv2(out)
        out = self.bn2(out)
        out += residual # Skip connection (O segredo das redes profundas)
        out = self.relu(out)
        return out

class NeuroCNCModel(nn.Module):
    def __init__(self, num_sensors=5, static_features=3):
        super(NeuroCNCModel, self).__init__()
        
        # --- Parte 1: Processamento Temporal (Sensores) ---
        # Camada de Entrada (1)
        self.initial_conv = nn.Conv1d(num_sensors, 64, kernel_size=7, padding=3)
        self.bn_initial = nn.BatchNorm1d(64)
        self.relu = nn.ReLU()
        
        # O "Core" Profundo: 16 Blocos Residuais x 2 Camadas cada = 32 Camadas
        # Camadas 2 a 33
        self.res_blocks = nn.Sequential(
            *[ResidualBlock(64) for _ in range(16)]
        )
        
        # Pooling para transformar tempo em vetor fixo (Camada 34)
        self.global_pool = nn.AdaptiveAvgPool1d(1)
        
        # --- Parte 2: Fusão com Dados Estáticos (Material, Ferramenta) ---
        # Camadas Densas para dados estáticos (Camadas 35-37)
        self.static_mlp = nn.Sequential(
            nn.Linear(static_features, 16),
            nn.ReLU(),
            nn.Linear(16, 32),
            nn.ReLU()
        )
        
        # --- Parte 3: O Decisor (Fully Connected Decoder) ---
        # Fusão: 64 (do tempo) + 32 (do estático) = 96 features
        # Camadas 38 a 50+
        self.decoder = nn.Sequential(
            nn.Linear(96, 256),   # Camada 38
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, 256),  # Camada 39
            nn.ReLU(),
            nn.Linear(256, 128),  # Camada 40
            nn.ReLU(),
            nn.Linear(128, 128),  # Camada 41
            nn.ReLU(),
            nn.Linear(128, 64),   # Camada 42
            nn.ReLU(),
            nn.Linear(64, 64),    # Camada 43
            nn.LeakyReLU(),
            nn.Linear(64, 32),    # Camada 44
            nn.Linear(32, 16),    # Camada 45
            nn.Linear(16, 8),     # Camada 46
            nn.Linear(8, 4),      # Camada 47
            nn.Linear(4, 1)       # Camada 48 (Saída: Offset em mm)
        )
        # Nota: Com BatchNorms e Ativações, tecnicamente passamos de 50 operações.

    def forward(self, x_sensor, x_static):
        # x_sensor shape: [Batch, Channels, Time]
        out_t = self.initial_conv(x_sensor)
        out_t = self.bn_initial(out_t)
        out_t = self.relu(out_t)
        
        out_t = self.res_blocks(out_t)
        out_t = self.global_pool(out_t)
        out_t = out_t.view(out_t.size(0), -1) # Flatten
        
        # Processa estáticos
        out_s = self.static_mlp(x_static)
        
        # Concatena
        combined = torch.cat((out_t, out_s), dim=1)
        
        # Decisão final
        prediction = self.decoder(combined)
        return prediction

# Teste rápido para validar 
if __name__ == "__main__":
    model = NeuroCNCModel()
    print(model)
    print("Total Parameters:", sum(p.numel() for p in model.parameters()))