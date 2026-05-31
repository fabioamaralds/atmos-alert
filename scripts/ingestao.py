import ee
import pandas as pd
import requests
import zipfile
import io
import time

print("🚀 Iniciando Pipeline de Ingestão de Dados - AtmosAlert...")

# CONFIGURAÇÕES E AUTENTICAÇÃO
# Inicializando o Google Earth Engine
ee.Initialize(project='atmosalert-497701')

# Dicionário Mestre Nacional: Top 1 Município por Estado (Agosto/2023)
cidades_alvo = {
    'FEIJO': {'uf': 'AC', 'lat': -8.1642, 'lon': -70.3536},
    'PENEDO': {'uf': 'AL', 'lat': -10.2905, 'lon': -36.5856},
    'TARTARUGALZINHO': {'uf': 'AP', 'lat': 1.5074, 'lon': -50.9168},
    'LABREA': {'uf': 'AM', 'lat': -7.2597, 'lon': -64.7975},
    'COCOS': {'uf': 'BA', 'lat': -14.1806, 'lon': -44.5381},
    'CAUCAIA': {'uf': 'CE', 'lat': -3.7328, 'lon': -38.6531},
    'BRASILIA': {'uf': 'DF', 'lat': -15.7975, 'lon': -47.8919},
    'SAO MATEUS': {'uf': 'ES', 'lat': -18.7161, 'lon': -39.8589},
    'MIMOSO DE GOIAS': {'uf': 'GO', 'lat': -15.0567, 'lon': -48.1619},
    'MIRADOR': {'uf': 'MA', 'lat': -6.3725, 'lon': -44.3631},
    'COLNIZA': {'uf': 'MT', 'lat': -9.4122, 'lon': -59.3364},
    'CORUMBA': {'uf': 'MS', 'lat': -19.0092, 'lon': -57.6533},
    'FRANCISCO DUMONT': {'uf': 'MG', 'lat': -17.2997, 'lon': -43.8569},
    'ALTAMIRA': {'uf': 'PA', 'lat': -3.2033, 'lon': -52.2064},
    'CAJAZEIRAS': {'uf': 'PB', 'lat': -6.8894, 'lon': -38.5606},
    'PRUDENTOPOLIS': {'uf': 'PR', 'lat': -25.2131, 'lon': -50.9778},
    'BODOCO': {'uf': 'PE', 'lat': -7.7778, 'lon': -39.9389},
    'URUCUI': {'uf': 'PI', 'lat': -7.2319, 'lon': -44.5561},
    'CAMPOS DOS GOYTACAZES': {'uf': 'RJ', 'lat': -21.7539, 'lon': -41.3236},
    'MOSSORO': {'uf': 'RN', 'lat': -5.1881, 'lon': -37.3442},
    'SAO FRANCISCO DE PAULA': {'uf': 'RS', 'lat': -29.4447, 'lon': -50.5842},
    'PORTO VELHO': {'uf': 'RO', 'lat': -8.7611, 'lon': -63.9004},
    'PACARAIMA': {'uf': 'RR', 'lat': 4.4756, 'lon': -61.1469},
    'LAGES': {'uf': 'SC', 'lat': -27.8106, 'lon': -50.3261},
    'SANTA ISABEL': {'uf': 'SP', 'lat': -23.3156, 'lon': -46.2214},
    'TOBIAS BARRETO': {'uf': 'SE', 'lat': -11.1844, 'lon': -37.9969},
    'LAGOA DA CONFUSAO': {'uf': 'TO', 'lat': -10.7936, 'lon': -49.6225}
}

# Período de Análise
mes_alvo = '2023-08'
nasa_inicio, nasa_fim = '20230801', '20230831'
ee_inicio, ee_fim = '2023-08-01', '2023-08-31'

# DataFrames vazios para acumularmos os dados
df_queimadas_final = pd.DataFrame()
df_vento_final = pd.DataFrame()
df_fumaca_final = pd.DataFrame()

# INGESTÃO: INPE (Focos de Calor)
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
                        
                        # 1. Converte para maiúsculo
                        df_uf['municipio'] = df_uf['municipio'].str.upper()

                        # 2. Remove todos os acentos, cedilhas e caracteres especiais
                        df_uf['municipio'] = (df_uf['municipio']
                                              .str.normalize('NFKD')
                                              .str.encode('ascii', errors='ignore')
                                              .str.decode('utf-8'))
                        
                        # 3. Extração da data
                        df_uf['Data'] = pd.to_datetime(df_uf['datahora']).dt.strftime('%Y-%m-%d')
                        df_uf_agosto = df_uf[df_uf['Data'].str.startswith(mes_alvo)]
                        
                        # 4. Junta ao DF principal
                        df_queimadas_final = pd.concat([df_queimadas_final, df_uf_agosto], ignore_index=True)

# Mantém apenas as cidades alvo
cidades_nomes = list(cidades_alvo.keys())
df_queimadas_final = df_queimadas_final[df_queimadas_final['municipio'].isin(cidades_nomes)]

# INGESTÃO: NASA POWER (Ventos)
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
        
    # Pausa para não ser bloqueado:
    time.sleep(2)

# INGESTÃO: COPERNICUS S-5P (Fumaça)
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

# SALVANDO OS DADOS BRUTOS (RAW)
print("\n💾 Salvando arquivos CSV na pasta 'data/raw/'...")
# *Nota: Garanta que a pasta '../data/raw/' existe no seu Ubuntu
df_queimadas_final.to_csv('../data/raw/bdqueimadas_agosto_2023.csv', index=False)
df_vento_final.to_csv('../data/raw/vento_nasa_agosto_2023.csv', index=False)
df_fumaca_final.to_csv('../data/raw/fumaca_copernicus_agosto_2023.csv', index=False)

print("Pipeline de Ingestão Finalizado com Sucesso! Bases reais prontas para limpeza e merge.")