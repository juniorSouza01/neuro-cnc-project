import torch
import torch.nn as nn

class ResidualBlock(nn.Module):
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
        out += residual 
        out = self.relu(out)
        return out

class NeuroCNCModel(nn.Module):
    def __init__(self, num_sensors=2, static_features=3): # Ajustado para 2 sensores
        super(NeuroCNCModel, self).__init__()
        
        self.initial_conv = nn.Conv1d(num_sensors, 64, kernel_size=7, padding=3)
        self.bn_initial = nn.BatchNorm1d(64)
        self.relu = nn.ReLU()
        
        # Reduzido para 4 blocos para ser mais leve no MVP (pode aumentar depois)
        self.res_blocks = nn.Sequential(*[ResidualBlock(64) for _ in range(4)])
        
        self.global_pool = nn.AdaptiveAvgPool1d(1)
        
        self.static_mlp = nn.Sequential(
            nn.Linear(static_features, 16),
            nn.ReLU(),
            nn.Linear(16, 32),
            nn.ReLU()
        )
        
        self.decoder = nn.Sequential(
            nn.Linear(96, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1) # Saída: Offset em mm
        )

    def forward(self, x_sensor, x_static):
        out_t = self.initial_conv(x_sensor)
        out_t = self.bn_initial(out_t)
        out_t = self.relu(out_t)
        out_t = self.res_blocks(out_t)
        out_t = self.global_pool(out_t)
        out_t = out_t.view(out_t.size(0), -1)
        
        out_s = self.static_mlp(x_static)
        combined = torch.cat((out_t, out_s), dim=1)
        return self.decoder(combined)