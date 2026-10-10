# Estação de Campo no TinkerCad — Montagem e Sensores

Circuito Arduino que representa uma estação de campo do AgroSmart (talhão `TAL-TC`). Código:
[`agrosmart_tinkercad.ino`](agrosmart_tinkercad.ino).

## Sensores utilizados

| Sensor (nome no TinkerCad) | Grandeza | Pino | Conversão no código | Uso na solução |
|---|---|---|---|---|
| **Sensor de temperatura [TMP36]** | Temperatura do ar (°C) | A0 | `(leitura × 5/1023 − 0,5) × 100` | Estresse térmico, risco de geada |
| **Sensor de umidade do solo** (Soil Moisture Sensor) | Umidade do solo (%) | A1 | `map(leitura, 0, 876, 0, 100)` | Déficit hídrico, acionamento da irrigação |
| **Fotorresistor (LDR)** + resistor 10 kΩ | Luminosidade (%) | A2 | `leitura × 100/1023` | Distinguir dia/noite; incidência solar |
| **Sensor PIR** | Movimento (0/1) | D2 | leitura digital | Evento: animal, praga noturna ou invasão |

## Atuadores (automação local)

| Componente | Pino | Comportamento |
|---|---|---|
| LED verde + resistor 220 Ω | D11 | Aceso quando o status é NORMAL |
| LED amarelo + resistor 220 Ω | D12 | Aceso em ATENÇÃO (umidade < 30%, temp. > 35 °C ou < 12 °C, ou movimento) |
| LED vermelho + resistor 220 Ω | D13 | Aceso em CRÍTICO (umidade < 20% ou movimento à noite) |
| LED azul + resistor 220 Ω | D10 | "Bomba de irrigação": liga com umidade < 30% e só desliga acima de 45% (histerese) |
| Piezo | D8 | Bipe de 1 kHz em situação crítica |

## Montagem passo a passo

1. Acesse <https://www.tinkercad.com> → **Circuits** → **Create new Circuit**.
2. Arraste um **Arduino Uno R3** e uma **placa de ensaio (breadboard)**.
3. Ligue o **5V** do Arduino ao barramento **+** da placa e o **GND** ao barramento **−**.
4. **TMP36** (pinos da esquerda para a direita, com a face plana para você): `+Vs` → 5V,
   `Vout` → **A0**, `GND` → GND.
5. **Sensor de umidade do solo**: `VCC` → 5V, `GND` → GND, `SIG` → **A1**.
6. **Fotorresistor**: um terminal → 5V; o outro terminal → **A2** *e* a um resistor de
   **10 kΩ** que vai ao GND (divisor de tensão).
7. **Sensor PIR**: `Power` → 5V, `Ground` → GND, `Signal` → **D2**.
8. **LEDs**: anodo (perna dobrada) → pino (D13 vermelho, D12 amarelo, D11 verde, D10 azul);
   catodo → resistor de **220 Ω** → GND.
9. **Piezo**: positivo → **D8**, negativo → GND.
10. Clique em **Code** → mude de "Blocks" para **Text** → apague tudo e cole o conteúdo de
    `agrosmart_tinkercad.ino`.
11. Clique em **Start Simulation** e abra o **Serial Monitor** (botão no rodapé do painel de código).

## Roteiro de teste no TinkerCad (gera dados para todos os status)

Com a simulação rodando, clique em cada sensor para mostrar o controle deslizante:

| Passo | Ação no sensor | Resultado esperado |
|---|---|---|
| 1 | Umidade do solo alta (~50%), temperatura ~25 °C, luz alta | LED **verde**; serial `...,NORMAL` |
| 2 | Abaixe a umidade do solo para ~25% | LED **amarelo** + LED **azul** (irrigação ligada); `irrigacao_ligada=1`, `ATENCAO` |
| 3 | Abaixe a umidade para ~15% | LED **vermelho** + **buzzer**; `CRITICO` |
| 4 | Suba a umidade para ~35% | Vermelho apaga, mas **azul continua** (histerese: só desliga acima de 45%) |
| 5 | Suba a umidade para > 45% | LED azul apaga |
| 6 | Suba a temperatura acima de 35 °C | LED **amarelo**; `ATENCAO` |
| 7 | Abaixe a luz (< 10%) e mova o objeto na frente do PIR | LED **vermelho** (movimento noturno); `CRITICO` |
| 8 | Temperatura abaixo de 12 °C | LED **amarelo** |

## Levando os dados do TinkerCad para a plataforma

1. Deixe a simulação rodar enquanto executa o roteiro acima (~40 s já bastam).
2. No Serial Monitor, selecione todo o texto e copie (Ctrl/Cmd + C).
3. Cole em `dados/raw/tinkercad_serial.txt`, **mantendo a linha de cabeçalho**
   (`millis,talhao_id,...`) na primeira linha. O repositório já traz uma captura de exemplo nesse formato.
4. Rode `python run_plataforma.py` — as leituras aparecem como talhão `TAL-TC` no processamento,
   nos alertas e na aba **Estação TinkerCad** do dashboard.

## Exemplo de dados gerados (saída serial)

```
millis,talhao_id,temperatura_c,umidade_solo_pct,luminosidade_pct,movimento_detectado,irrigacao_ligada,status
0,TAL-TC,24.7,52.3,78.4,0,0,NORMAL
10022,TAL-TC,27.7,28.7,80.1,0,1,ATENCAO
18040,TAL-TC,37.1,18.5,82.5,0,1,CRITICO
22049,TAL-TC,33.2,33.9,60.2,0,1,NORMAL
30067,TAL-TC,17.8,46.9,5.3,1,0,CRITICO
36081,TAL-TC,11.4,46.5,5.3,0,0,ATENCAO
```

Repare na linha `22049`: a umidade já voltou para 33,9% (status NORMAL), mas a irrigação
continua ligada por causa da histerese — ela só desliga acima de 45%.
