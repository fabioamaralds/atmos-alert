import os
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv

# Carrega as variáveis de ambiente
load_dotenv()

print("Iniciando Pipeline de Processamento e Transformação - AtmosAlert...")

# Estabelece a conexão com o Supabase logo no início
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("ERRO: Variável 'DATABASE_URL' não encontrada. Verifique os Secrets do GitHub ou o seu .env local!")

engine = create_engine(DATABASE_URL, poolclass=NullPool)

# CARREGAMENTO DOS DADOS BRUTOS (DIRETO DO SUPABASE)
print(" -> Lendo tabelas brutas (RAW) do Supabase...")
with engine.begin() as conn:
    df_queimadas = pd.read_sql_table('raw_bdqueimadas', conn)
    df_fumaca = pd.read_sql_table('raw_fumaca_copernicus', conn)
    df_vento = pd.read_sql_table('raw_vento_nasa', conn)

# Garantindo que as datas estejam no formato correto após virem do banco
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
print(" -> Inserindo Tabela Analítica Consolidada (tb_atmosalert_analitico) no Supabase...")
with engine.begin() as conn:
    # Salva no banco a tabela mastigada final
    df_atmosalert.to_sql('tb_atmosalert_analitico', conn, if_exists='replace', index=False)
    
print("Sucesso! A tabela unificada foi carregada no Supabase e está pronta para o Dashboard.")
print("\n Pipeline de Processamento Finalizado!")