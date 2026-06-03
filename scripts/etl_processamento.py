import os
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv

# Carrega as variáveis de ambiente (onde está a sua DATABASE_URL)
load_dotenv()

print("⚙️ Iniciando Pipeline de Processamento e Transformação - AtmosAlert...")

# CARREGAMENTO DOS DADOS BRUTOS
print(" -> Lendo arquivos brutos (RAW)...")
caminho_queimadas = '../data/raw/bdqueimadas_agosto_2023.csv'
caminho_fumaca = '../data/raw/fumaca_copernicus_agosto_2023.csv'
caminho_vento = '../data/raw/vento_nasa_agosto_2023.csv'

df_queimadas = pd.read_csv(caminho_queimadas)
df_fumaca = pd.read_csv(caminho_fumaca)
df_vento = pd.read_csv(caminho_vento)

# Garantindo que as datas estejam no formato correto
df_queimadas['Data'] = pd.to_datetime(df_queimadas['Data'])
df_fumaca['Data'] = pd.to_datetime(df_fumaca['Data'])
df_vento['Data'] = pd.to_datetime(df_vento['Data'])

# Padronizando colunas
if 'municipio' in df_queimadas.columns:
    df_queimadas.rename(columns={'municipio': 'Municipio'}, inplace=True)

# TRANSFORMAÇÃO E AGREGAÇÃO (A Lógica de Negócio)
print(" -> Aplicando tratamentos e agregações...")

# Fumaça: Tira a média em caso de leituras duplicadas do satélite no mesmo dia
df_fumaca_tratado = (df_fumaca
                     .groupby(['Data', 'Municipio'], as_index=False)
                     .agg({'Indice_Fumaca': 'mean'}))

# Queimadas: Conta os focos de calor por dia e município
df_queimadas_agrupado = (df_queimadas
                         .groupby(['Data', 'Municipio'])
                         .size()
                         .reset_index(name='Focos_Calor'))

# MERGE: CRIANDO A BASE UNIFICADA
print(" -> Cruzando as bases de dados (Merge)...")
df_consolidado = pd.merge(df_fumaca_tratado, df_vento, on=['Data', 'Municipio'], how='inner')
df_atmosalert = pd.merge(df_consolidado, df_queimadas_agrupado, on=['Data', 'Municipio'], how='left')

# Preenche dias sem fogo com zero e ajusta ordenação
df_atmosalert['Focos_Calor'] = df_atmosalert['Focos_Calor'].fillna(0).astype(int)
df_atmosalert = df_atmosalert.sort_values(by=['Municipio', 'Data']).reset_index(drop=True)

# CÁLCULO DE ANOMALIAS E ALERTAS (O Motor do Sistema)
print(" -> Calculando gatilhos estatísticos (IQR e Score Z)...")

# Alerta Laranja (IQR)
Q1 = df_atmosalert['Indice_Fumaca'].quantile(0.25)
Q3 = df_atmosalert['Indice_Fumaca'].quantile(0.75)
IQR = Q3 - Q1
limite_superior_iqr = Q3 + 1.5 * IQR
df_atmosalert['Alerta_IQR'] = df_atmosalert['Indice_Fumaca'] > limite_superior_iqr

# Alerta Vermelho (Score Z)
media_fumaca = df_atmosalert['Indice_Fumaca'].mean()
std_fumaca = df_atmosalert['Indice_Fumaca'].std()
df_atmosalert['Score_Z_Fumaca'] = (df_atmosalert['Indice_Fumaca'] - media_fumaca) / std_fumaca
limite_z = 3.0
df_atmosalert['Alerta_Z'] = df_atmosalert['Score_Z_Fumaca'] > limite_z

# CARGA NO BANCO DE DADOS (SUPABASE)
print("\n ☁️ Iniciando conexão com o banco de dados Supabase...")
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("ERRO: Variável 'DATABASE_URL' não encontrada. Verifique o arquivo .env!")
else:
    try:
        # Cria a conexão com o banco usando NullPool (melhor para scripts curtos/serverless)
        engine = create_engine(DATABASE_URL, poolclass=NullPool)
        
        with engine.begin() as conn:
            print("  -> Inserindo Tabela Analítica Consolidada (tb_atmosalert_analitico)...")
            # Salva no banco. O if_exists='replace' recria a tabela para testes.
            df_atmosalert.to_sql('tb_atmosalert_analitico', conn, if_exists='replace', index=False)
            
        print("Sucesso! A tabela unificada foi carregada no Supabase e está pronta para o Dashboard.")
        
    except Exception as e:
        print(f"Erro ao enviar para o banco de dados: {e}")

print("\n Pipeline de Processamento Finalizado!")