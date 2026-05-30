import ee
import pandas as pd
import requests
import zipfile
import io

print("🚀 Iniciando Pipeline de Ingestão de Dados - AtmosAlert...")

# ==========================================
# 0. CONFIGURAÇÕES E AUTENTICAÇÃO
# ==========================================
# Inicializando o Google Earth Engine
ee.Initialize(project='atmosalert-497701')

# Dicionário mestre com as cidades, estados e coordenadas (Lat, Lon)
cidades_alvo = {
    'PORTO VELHO': {'uf': 'RO', 'lat': -8.7611, 'lon': -63.9004},
    'CUIABA': {'uf': 'MT', 'lat': -15.6014, 'lon': -56.0978},
    'BARREIRAS': {'uf': 'BA', 'lat': -12.1527, 'lon': -44.9902},
    'CAMPINAS': {'uf': 'SP', 'lat': -22.9099, 'lon': -47.0626},
    'RIBEIRAO PRETO': {'uf': 'SP', 'lat': -21.1704, 'lon': -47.8103},
    'LONDRINA': {'uf': 'PR', 'lat': -23.3102, 'lon': -51.1627}
}

# Período de Análise
mes_alvo = '2023-08'
nasa_inicio, nasa_fim = '20230801', '20230831'
ee_inicio, ee_fim = '2023-08-01', '2023-08-31'

# DataFrames vazios para acumularmos os dados
df_queimadas_final = pd.DataFrame()
df_vento_final = pd.DataFrame()
df_fumaca_final = pd.DataFrame()

# ==========================================
# 1. INGESTÃO: INPE (Focos de Calor)
# ==========================================
print("\n🔥 [1/3] Extraindo Focos de Calor (INPE)...")
ufs_unicas = set([info['uf'] for info in cidades_alvo.values()])

for uf in ufs_unicas:
    url_inpe = f"https://dataserver-coids.inpe.br/queimadas/queimadas/focos/csv/anual/EstadosBr_sat_ref/{uf}/focos_br_{uf.lower()}_ref_2023.zip"
    res = requests.get(url_inpe)
    
    if res.status_code == 200:
        with zipfile.ZipFile(io.BytesIO(res.content)) as z:
                    csv_name = z.namelist()[0]
                    with z.open(csv_name) as f:
                        # O sep=None ajuda a evitar problemas com vírgulas e pontos e vírgulas
                        df_uf = pd.read_csv(f, sep=None, engine='python')
                        
                        # 1. Normalização das colunas
                        df_uf.columns = df_uf.columns.str.lower().str.strip()
                        
                        # 2. O Pulo do Gato: Padronizando o nome da coluna de data
                        if 'data_pas' in df_uf.columns:
                            df_uf.rename(columns={'data_pas': 'datahora'}, inplace=True)
                        elif 'data_hora' in df_uf.columns:
                            df_uf.rename(columns={'data_hora': 'datahora'}, inplace=True)
                        
                        df_uf['municipio'] = df_uf['municipio'].str.upper()
                        
                        # 3. Extração da data
                        df_uf['Data'] = pd.to_datetime(df_uf['datahora']).dt.strftime('%Y-%m-%d')
                        df_uf_agosto = df_uf[df_uf['Data'].str.startswith(mes_alvo)]
                        
                        # 4. Junta ao DF principal
                        df_queimadas_final = pd.concat([df_queimadas_final, df_uf_agosto], ignore_index=True)

# Mantém apenas as cidades alvo
cidades_nomes = list(cidades_alvo.keys())
df_queimadas_final = df_queimadas_final[df_queimadas_final['municipio'].isin(cidades_nomes)]

# ==========================================
# 2. INGESTÃO: NASA POWER (Ventos)
# ==========================================
print("\n💨 [2/3] Extraindo Velocidade e Direção do Vento (NASA)...")
for cidade, info in cidades_alvo.items():
    url_nasa = f"https://power.larc.nasa.gov/api/temporal/daily/point?parameters=WS50M,WD50M&community=RE&longitude={info['lon']}&latitude={info['lat']}&start={nasa_inicio}&end={nasa_fim}&format=JSON"
    res = requests.get(url_nasa)
    
    if res.status_code == 200:
        dados = res.json()['properties']['parameter']
        df_temp = pd.DataFrame({
            'Data_Bruta': list(dados['WS50M'].keys()),
            'Velocidade_Vento_50m': list(dados['WS50M'].values()),
            'Direcao_Vento_50m': list(dados['WD50M'].values())
        })
        df_temp['Data'] = pd.to_datetime(df_temp['Data_Bruta'], format='%Y%m%d').dt.strftime('%Y-%m-%d')
        df_temp['Municipio'] = cidade
        df_temp = df_temp.drop(columns=['Data_Bruta'])
        
        df_vento_final = pd.concat([df_vento_final, df_temp], ignore_index=True)

# ==========================================
# 3. INGESTÃO: COPERNICUS S-5P (Fumaça)
# ==========================================
print("\n🌫️ [3/3] Extraindo Índice de Aerossóis (Google Earth Engine)...")
s5p_colecao = (ee.ImageCollection('COPERNICUS/S5P/OFFL/L3_AER_AI')
               .filterDate(ee_inicio, ee_fim)
               .select('absorbing_aerosol_index'))

for cidade, info in cidades_alvo.items():
    ponto = ee.Geometry.Point([info['lon'], info['lat']])
    
    def extrair_valor(imagem):
        dict_valor = imagem.reduceRegion(reducer=ee.Reducer.mean(), geometry=ponto, scale=1113.2, bestEffort=True)
        return ee.Feature(None, {
            'Data': imagem.date().format('YYYY-MM-dd'),
            'Indice_Fumaca': dict_valor.get('absorbing_aerosol_index'),
            'Municipio': cidade
        })
    
    # Extrai, converte nativamente para evitar erro de geemap e joga no DF
    dados_brutos = s5p_colecao.map(extrair_valor).getInfo()
    lista_dados = [feat['properties'] for feat in dados_brutos['features']]
    df_temp = pd.DataFrame(lista_dados).dropna()
    
    df_fumaca_final = pd.concat([df_fumaca_final, df_temp], ignore_index=True)

# ==========================================
# 4. SALVANDO OS DADOS BRUTOS (RAW)
# ==========================================
print("\n💾 Salvando arquivos CSV na pasta 'data/raw/'...")
# *Nota: Garanta que a pasta '../data/raw/' existe no seu Ubuntu
df_queimadas_final.to_csv('../data/raw/bdqueimadas_agosto_2023.csv', index=False)
df_vento_final.to_csv('../data/raw/vento_nasa_agosto_2023.csv', index=False)
df_fumaca_final.to_csv('../data/raw/fumaca_copernicus_agosto_2023.csv', index=False)

print("✅ Pipeline de Ingestão Finalizado com Sucesso! Bases reais prontas para limpeza e merge.")