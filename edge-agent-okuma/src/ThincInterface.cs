using System;
// using Okuma.CLDATAPI.DataAPI; // Descomentar na máquina real

namespace NeuroEdge.MachineInterface
{
    public class ThincInterface
    {
        // private CVariables _commonVariables; // Objeto da API Okuma
        // private CMachine _machine;

        public ThincInterface()
        {
            // Na maquina real:
            // _commonVariables = new CVariables();
            // _machine = new CMachine();
        }

        public void Connect()
        {
            Console.WriteLine("Inicializando THINC API...");
            // Em ambiente de teste (seu PC), não faz nada. 
            // Na máquina: _commonVariables.Open();
        }

        public double GetSpindleLoad()
        {
            // Retorna carga do eixo S (Spindle)
            // Na real: return _machine.GetLoadMeter(Axis.Spindle);
            
            // Simulação para teste:
            Random rnd = new Random();
            return 20.0 + (rnd.NextDouble() * 5.0); 
        }

        public double GetTemperature()
        {
            // Na real: Leitura de sensor via API ou I/O
            return 45.5; // Graus Celsius
        }

        public double ReadVariable(string varName)
        {
            // Ex: Lê VC100
            // int index = int.Parse(varName.Replace("VC", ""));
            // return _commonVariables.GetCommonVariable(index);
            return 0.0;
        }

        public void WriteVariable(string varName, double value)
        {
            // int index = int.Parse(varName.Replace("VC", ""));
            // _commonVariables.SetCommonVariable(index, value);
            Console.WriteLine($"[THINC API] Escrevendo {value} em {varName}");
        }
    }
}