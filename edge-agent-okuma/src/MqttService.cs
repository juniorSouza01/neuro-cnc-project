using System;
using System.Text;
using System.Threading.Tasks;
using MQTTnet;
using MQTTnet.Client;
using MQTTnet.Client.Options;
using Newtonsoft.Json; // Instale via NuGet

namespace NeuroEdge.Communication
{
    public class MqttService
    {
        private IMqttClient _mqttClient;
        private IMqttClientOptions _options;
        private string _topicCommand = "machine/okuma01/command";
        private string _topicTelemetry = "machine/okuma01/telemetry";

        // Evento para quando a IA mandar corrigir
        public event Action<string, double> OnCorrectionReceived;

        public MqttService(string brokerIp)
        {
            var factory = new MqttFactory();
            _mqttClient = factory.CreateMqttClient();

            _options = new MqttClientOptionsBuilder()
                .WithTcpServer(brokerIp, 1883) // Porta padrão do Mosquitto
                .WithClientId("OkumaEdgeAgent")
                .WithCleanSession()
                .Build();

            _mqttClient.UseApplicationMessageReceivedHandler(e => HandleMessage(e));
        }

        public async Task ConnectAsync()
        {
            Console.WriteLine("Conectando ao MQTT Broker...");
            await _mqttClient.ConnectAsync(_options, System.Threading.CancellationToken.None);
            
            // Assinar tópico de comandos da IA
            await _mqttClient.SubscribeAsync(new MqttTopicFilterBuilder().WithTopic(_topicCommand).Build());
            Console.WriteLine("Conectado e assinando tópicos.");
        }

        public async Task PublishTelemetry(object data)
        {
            if (!_mqttClient.IsConnected) return;

            string json = JsonConvert.SerializeObject(data);
            var message = new MqttApplicationMessageBuilder()
                .WithTopic(_topicTelemetry)
                .WithPayload(json)
                .WithQualityOfServiceLevel(MQTTnet.Protocol.MqttQualityOfServiceLevel.AtLeastOnce)
                .Build();

            await _mqttClient.PublishAsync(message);
        }

        private void HandleMessage(MqttApplicationMessageReceivedEventArgs e)
        {
            try
            {
                string payload = Encoding.UTF8.GetString(e.ApplicationMessage.Payload);
                dynamic command = JsonConvert.DeserializeObject(payload);

                string targetVar = command.target_var; // Ex: "VC100"
                double value = command.value;          // Ex: 0.015

                OnCorrectionReceived?.Invoke(targetVar, value);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Erro ao processar mensagem MQTT: {ex.Message}");
            }
        }
    }
}