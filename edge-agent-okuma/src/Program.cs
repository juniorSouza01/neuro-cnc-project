using System;
using System.Threading;
using NeuroEdge.Communication;
using NeuroEdge.MachineInterface;
using NeuroEdge.Safety;

namespace NeuroEdge
{
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("Neuro-CNC Agent Iniciando...");

            // 1. Conexão com a Máquina (API THINC)
            var cnc = new ThincInterface();
            cnc.Connect();

            // 2. Conexão MQTT com o Servidor Docker
            var mqtt = new MqttService("192.168.1.100"); // IP do seu PC Servidor
            mqtt.ConnectAsync().Wait();

            // 3. Registrar Callback: O que fazer quando a IA manda um comando?
            mqtt.OnCorrectionReceived += (targetVar, value) => 
            {
                Console.WriteLine($"Comando IA Recebido: {targetVar} = {value}");
                
                // --- SEGURANÇA (SAFETY GUARD) ---
                if (SafetyGuard.IsSafe(value))
                {
                    double currentVal = cnc.ReadVariable(targetVar);
                    double newVal = currentVal + value;
                    
                    cnc.WriteVariable(targetVar, newVal);
                    Console.WriteLine($"SUCESSO: {targetVar} ajustado para {newVal}");
                }
                else
                {
                    Console.WriteLine("PERIGO: Correção ignorada pelo Safety Guard.");
                }
            };

            // 4. Loop de Telemetria (Envia dados para a IA aprender)
            while (true)
            {
                var telemetry = new 
                {
                    spindle_load = cnc.GetSpindleLoad(),
                    temp = cnc.GetTemperature(),
                    timestamp = DateTime.UtcNow
                };

                mqtt.PublishTelemetry(telemetry);
                Thread.Sleep(100); // 10Hz
            }
        }
    }
}