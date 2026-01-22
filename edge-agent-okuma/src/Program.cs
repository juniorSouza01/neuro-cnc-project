using System;
using System.Threading;
using System.Threading.Tasks;
using NeuroEdge.Communication;
using NeuroEdge.MachineInterface;
using NeuroEdge.Safety;

namespace NeuroEdge
{
    class Program
    {
        static async Task Main(string[] args)
        {
            Console.WriteLine("--- NEURO-CNC AGENT STARTING (Okuma OSP Env) ---");

            var cnc = new ThincInterface();
            cnc.Connect();

            // Usar localhost se rodando fora do docker, ou IP da rede
            var mqtt = new MqttService("localhost"); 
            await mqtt.ConnectAsync();

            mqtt.OnCorrectionReceived += (targetVar, value) => 
            {
                Console.WriteLine($"\n[COMANDO RECEBIDO] Alvo: {targetVar} | Ajuste: {value}mm");
                
                if (SafetyGuard.IsSafe(value))
                {
                    double currentVal = cnc.ReadVariable(targetVar);
                    double newVal = currentVal + value;
                    cnc.WriteVariable(targetVar, newVal);
                    
                    Console.ForegroundColor = ConsoleColor.Green;
                    Console.WriteLine($"[SUCESSO] Compensação Aplicada. Novo {targetVar}: {newVal}");
                    Console.ResetColor();
                }
                else
                {
                    Console.ForegroundColor = ConsoleColor.Red;
                    Console.WriteLine("[BLOQUEIO] SafetyGuard impediu o movimento.");
                    Console.ResetColor();
                }
            };

            // Simulação do Ciclo de Usinagem
            Console.WriteLine("Iniciando monitoramento de ciclo...");
            
            while (true)
            {
                // Simula variação de carga durante corte
                var telemetry = new 
                {
                    spindle_load = cnc.GetSpindleLoad(),
                    temp = cnc.GetTemperature(),
                    timestamp = DateTime.UtcNow.ToString("o"),
                    run_id = 101 // Ciclo fixo para teste
                };

                await mqtt.PublishTelemetry(telemetry);
                
                // Simulação visual no console
                if (telemetry.spindle_load > 24.0) Console.Write("#");
                else Console.Write(".");

                Thread.Sleep(100); 
            }
        }
    }
}