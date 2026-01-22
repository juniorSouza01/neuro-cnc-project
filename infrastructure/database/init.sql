-- Habilita Time-Series
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Tabela de Setup (Metadados da peça e contexto)
CREATE TABLE production_runs (
    run_id SERIAL PRIMARY KEY,
    part_program_name TEXT NOT NULL,
    material_code TEXT,
    tool_id TEXT,
    target_dimension_microns FLOAT,
    start_time TIMESTAMP DEFAULT NOW(),
    end_time TIMESTAMP
);

-- Tabela de Telemetria (Alta frequência: Sensores)
CREATE TABLE telemetry (
    time TIMESTAMP NOT NULL,
    run_id INT,
    spindle_load FLOAT,
    spindle_temp FLOAT,
    axis_x_load FLOAT,
    axis_z_load FLOAT,
    vibration_level FLOAT
);
-- Transforma em tabela temporal otimizada
SELECT create_hypertable('telemetry', 'time');

-- Tabela de Metrologia (O "Gabarito" da CMM)
CREATE TABLE metrology_results (
    id SERIAL PRIMARY KEY,
    run_id INT,
    measured_dimension_microns FLOAT,
    deviation_microns FLOAT, -- O erro (Target - Measured)
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Tabela de Ações da IA (Histórico de alterações)
CREATE TABLE ai_actions (
    id SERIAL PRIMARY KEY,
    run_id INT,
    suggested_offset_vc FLOAT,
    applied_offset_vc FLOAT,
    confidence_score FLOAT,
    timestamp TIMESTAMP DEFAULT NOW()
);