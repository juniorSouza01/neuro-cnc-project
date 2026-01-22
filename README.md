```markdown
# Como Executar o Projeto

### 1. Levantar a Infraestrutura
Abra o terminal na pasta `neuro-cnc/infrastructure` e execute:

```bash
docker-compose up --build
```
*Aguarde o banco de dados e o backend iniciarem.*

---

### 2. Iniciar o Agente (Simulador da Máquina)
Em um **novo terminal**, vá para `neuro-cnc/edge-agent-okuma` e execute:
*(Requer .NET 6.0+)*

```bash
dotnet run --project NeuroEdge.csproj
```
*O console mostrará "..." indicando que a máquina está rodando.*

---

### 3. Simular Metrologia (Enviar Erro)
Em outro terminal, envie este comando para simular um desvio de -7mm na peça:

```bash
curl -X POST http://localhost:8000/metrology \
     -H "Content-Type: application/json" \
     -d '{"part_id": "PECA-001", "measured_deviation": -7.0}'
```

---

### 4. Aprovar e Validar
1. Acesse o Dashboard: [http://localhost:8501](http://localhost:8501).
2. Veja a sugestão na tela e clique em **APLICAR CORREÇÃO**.
3. Verifique o terminal do **Passo 2** (Agente). Você verá:

```text
[COMANDO RECEBIDO] Alvo: VC100 | Ajuste: 7.0mm
[SUCESSO] Compensação Aplicada. Novo VC100: 7.0
```
```