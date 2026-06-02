# Premissas e Dicionário de Dados AtmosAlert

Com base nos dados adquiridos do INPE, Nasa Power e o Satélite Copernicus, foram adotadas as seguintes premissas:

---
## Escolha do período
A escolha de Agosto de 2023 como objeto de estudo baseia-se na identificação de um Cenário de Estresse Máximo. Este período concentrou o ápice da estiagem brasileira, agravada pelas anomalias climáticas do El Niño, gerando alta densidade de focos de calor. Analisar este período permite testar os limites e a eficácia do algoritmo preditivo do AtmosAlert sob as condições mais adversas de qualidade do ar.
Três fatores foram importantes na escolha desse período:

**1. O Ápice da Sazonalidade de Queimadas (A Estiagem):** No Brasil, o mês de agosto marca o pico do período de seca (estiagem). A umidade relativa do ar despenca e a vegetação fica extremamente inflamável. Historicamente, a janela entre agosto e setembro concentra os maiores índices de focos de calor registrados pelo INPE no ano inteiro. Escolher agosto é escolher o mês em que o problema que o AtmosAlert tenta resolver está mais latente.

**2. O Fator "El Niño" de 2023 (Anomalia Climática):** O ano de 2023 não foi um ano comum. Foi marcado pelo início de um forte fenômeno El Niño, que alterou drásticamente o clima no Brasil. Ele bloqueou as frentes frias no Sul e causou uma seca extrema e temperaturas recordes na Amazônia e no Centro-Oeste. Isso fez com que as queimadas em agosto de 2023 gerassem volumes anormais de fumaça, tornando os dados do satélite Sentinel-5P (Copernicus) muito mais evidentes e fáceis de serem correlacionados no seu modelo matemático.

**3. Inversão Térmica e Dinâmica dos Ventos:** Durante o mês de agosto (inverno no hemisfério sul), é muito comum a ocorrência de "bloqueios atmosféricos" e inversão térmica. Isso significa que o vento traz a fumaça das queimadas (Norte/Centro-Oeste) em direção ao Sudeste/Sul (fenômeno conhecido como "Rios Voadores" de fumaça), mas o ar frio próximo ao solo impede que essa poluição se dissipe. A fumaça fica "presa" em cima das cidades, o que causa a lotação imediata de hospitais e UBS com crises respiratórias.

---

## Dicionário de Dados
**1. Dados de Queimadas (bdqueimadas_agosto_2023.csv):** Este é o dataset de causa. Ele é o mais granular de todos, ou seja, cada linha representa um único foco de incêndio detectado pelo satélite em um momento específico.
- `id_bdq` e `foco_id`: São os identificadores únicos (RG) daquele incêndio específico no banco de dados do INPE;
- `lat` e `lon`: A latitude e longitude exatas de onde o fogo estava;
- `datahora`: O momento exato (dia, hora, minuto) em que o satélite passou por cima da coordenada e detectou o calor;
- `pais`, `estado`, `municipio`, `bioma`: Dados geográficos que confirmam onde o foco ocorreu;
- `Data`: Coluna padronizada (YYYY-MM-DD). Um município pode ter várias linhas. Isso significa que houveram vários focos de incêndio no mesmo dia.

**2. Dados de Fumaça/Aerossóis (fumaca_copernicus_agosto_2023.csv):** Este é o dataset de consequência (ou variável alvo/resposta). Ele mostra a média de poluição na atmosfera acima da cidade naquele dia.
- `Data` e `Municipio`: Chaves de cruzamento. Aqui temos apenas uma linha por dia para cada cidade;
- `Indice_Fumaca` (UV Aerosol Index): Este é o número mágico do satélite Sentinel-5P. Valores negativos ou muito próximos a zero (ex: -0.658 no dia 02/08): Indicam atmosfera limpa ou ausência de fumaça densa. Valores positivos altos (ex: 0.324 no dia 06/08): Indicam a presença forte de aerossóis absorventes na atmosfera (fumaça de queimada, fuligem ou poeira). Quanto maior o número, pior a qualidade do ar.

**3. Dados de Vento (vento_nasa_agosto_2023.csv):** Este é o dataset de transporte (o vetor que leva o problema de um lugar para o outro). Ele também possui uma linha por dia para cada cidade.
- `Velocidade_Vento_50m`: A velocidade do vento a 50 metros de altura (onde a fumaça costuma viajar), medida em metros por segundo (m/s).
- `Direcao_Vento_50m`: Medida em graus meteorológicos (de 0 a 360). Sendo 0 ou 360 = Norte, 90 = Leste, 180 = Sul e 270 = Oeste. Exemplo: No dia 01/08, a direção foi 249.7 (aproximadamente Oeste-Sudoeste). Isso ajuda a entender de qual região a fumaça está sendo trazida.
