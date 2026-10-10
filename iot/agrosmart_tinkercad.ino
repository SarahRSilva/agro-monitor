/*
 * AgroSmart — Estação de campo simulada (Fase 6)
 * Plataforma: Arduino Uno R3 (TinkerCad Circuits)
 *
 * Sensores (entradas):
 *   A0  -> TMP36            temperatura do ar (°C)
 *   A1  -> Soil Moisture    umidade do solo (%)
 *   A2  -> Fotorresistor    luminosidade (%) — divisor com resistor de 10 kΩ
 *   D2  -> Sensor PIR       evento de movimento (animal/praga/invasão)
 *
 * Atuadores (saídas — automação local, "edge"):
 *   D13 -> LED vermelho     alerta CRÍTICO
 *   D12 -> LED amarelo      alerta de ATENÇÃO/AVISO
 *   D11 -> LED verde        situação NORMAL
 *   D10 -> LED azul         bomba de irrigação ligada (simula relé)
 *   D8  -> Piezo (buzzer)   sinal sonoro de alerta crítico
 *
 * Saída serial (9600 baud), uma linha CSV a cada INTERVALO_MS:
 *   millis,talhao_id,temperatura_c,umidade_solo_pct,luminosidade_pct,movimento_detectado,irrigacao_ligada,status
 *
 * As linhas do Serial Monitor podem ser copiadas para
 * dados/raw/tinkercad_serial.txt e são lidas pelo processamento em Python.
 */

const char* TALHAO_ID = "TAL-TC";   // talhão representado pela estação TinkerCad

const int PINO_TEMP       = A0;
const int PINO_UMIDADE    = A1;
const int PINO_LUZ        = A2;
const int PINO_PIR        = 2;
const int LED_VERMELHO    = 13;
const int LED_AMARELO     = 12;
const int LED_VERDE       = 11;
const int LED_IRRIGACAO   = 10;
const int PINO_BUZZER     = 8;

// Limiares — os mesmos do motor de regras em Python (docker/api/regras.py da Fase 4,
// estendido em automacao/automacao_inteligente.py)
const float UMIDADE_LIGA_IRRIGACAO    = 30.0;  // liga bomba abaixo disso
const float UMIDADE_DESLIGA_IRRIGACAO = 45.0;  // histerese: desliga acima disso
const float UMIDADE_CRITICA           = 20.0;
const float TEMP_MAX                  = 35.0;
const float TEMP_MIN                  = 12.0;
const float LUZ_NOITE                 = 10.0;  // abaixo disso consideramos noite

// Leitura máxima do sensor de umidade do solo no TinkerCad (solo encharcado)
const int UMIDADE_LEITURA_MAX = 876;

const unsigned long INTERVALO_MS = 2000;

bool irrigacaoLigada = false;

void setup() {
  pinMode(PINO_PIR, INPUT);
  pinMode(LED_VERMELHO, OUTPUT);
  pinMode(LED_AMARELO, OUTPUT);
  pinMode(LED_VERDE, OUTPUT);
  pinMode(LED_IRRIGACAO, OUTPUT);
  pinMode(PINO_BUZZER, OUTPUT);

  Serial.begin(9600);
  Serial.println("millis,talhao_id,temperatura_c,umidade_solo_pct,luminosidade_pct,movimento_detectado,irrigacao_ligada,status");
}

float lerTemperatura() {
  // TMP36: 10 mV/°C com offset de 500 mV
  float tensao = analogRead(PINO_TEMP) * (5.0 / 1023.0);
  return (tensao - 0.5) * 100.0;
}

float lerUmidadeSolo() {
  int bruto = analogRead(PINO_UMIDADE);
  return constrain(map(bruto, 0, UMIDADE_LEITURA_MAX, 0, 1000), 0, 1000) / 10.0;
}

float lerLuminosidade() {
  return analogRead(PINO_LUZ) * 100.0 / 1023.0;
}

void loop() {
  float temperatura = lerTemperatura();
  float umidade     = lerUmidadeSolo();
  float luz         = lerLuminosidade();
  int movimento     = digitalRead(PINO_PIR);

  // Automação local de irrigação com histerese (evita liga/desliga contínuo)
  if (umidade < UMIDADE_LIGA_IRRIGACAO) {
    irrigacaoLigada = true;
  } else if (umidade > UMIDADE_DESLIGA_IRRIGACAO) {
    irrigacaoLigada = false;
  }

  // Classificação do status (mesma lógica do motor de regras em Python)
  bool critico = umidade < UMIDADE_CRITICA || (movimento == HIGH && luz < LUZ_NOITE);
  bool atencao = umidade < UMIDADE_LIGA_IRRIGACAO || temperatura > TEMP_MAX
                 || temperatura < TEMP_MIN || movimento == HIGH;

  const char* status = critico ? "CRITICO" : (atencao ? "ATENCAO" : "NORMAL");

  digitalWrite(LED_VERMELHO, critico);
  digitalWrite(LED_AMARELO, !critico && atencao);
  digitalWrite(LED_VERDE, !critico && !atencao);
  digitalWrite(LED_IRRIGACAO, irrigacaoLigada);

  if (critico) {
    tone(PINO_BUZZER, 1000, 300);
  } else {
    noTone(PINO_BUZZER);
  }

  Serial.print(millis());              Serial.print(',');
  Serial.print(TALHAO_ID);             Serial.print(',');
  Serial.print(temperatura, 1);        Serial.print(',');
  Serial.print(umidade, 1);            Serial.print(',');
  Serial.print(luz, 1);                Serial.print(',');
  Serial.print(movimento);             Serial.print(',');
  Serial.print(irrigacaoLigada ? 1 : 0); Serial.print(',');
  Serial.println(status);

  delay(INTERVALO_MS);
}
