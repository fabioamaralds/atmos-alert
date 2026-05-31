# AtmosAlert

Projeto desenvolvido para criação de uma solução de inteligência espacial voltada para a saúde urbana, antecipando crises respiratórias.
Este repositório contém apenas o código-fonte, documentação técnica e estrutura do projeto.

---

## 🎯 Objetivo do Projeto

Identificar e antecipar o risco de nuvens de poluição e aerossóis tóxicos nas cidades brasileiras, utilizando dados espaciais do INPE, NASA e Copernicus Sentinel-5P.  
Aplicação, tratamento e cálculos estatísticos (IQR e Score Z) em Python, armazenamento dos dados em banco PostgreSQL, hospedado no Supabase e visualizações estratégicas em dashboards interativos.

---

## 📂 Estrutura do Repositório

### Src e Scripts
Contém os códigos-fonte e scripts Python utilizados no projeto:

- Ingestão de dados das APIs (NASA, INPE, Copernicus)
- Cálculo das métricas de anomalias (Score Z e IQR)
- Integração e atualização do banco PostgreSQL no Supabase
- Funções auxiliares

Esses arquivos representam o núcleo técnico do projeto.

---

### Notebooks
Contém os arquivos de exploração e prototipagem:

- Análises exploratórias e limpeza inicial
- Testes de significância estatística (Pingouin)
- Geração de gráficos univariados e bivariados

---

### Docs
Documentação técnica do projeto e entrega:

- Regras matemáticas para disparo dos alertas
- Dicionário de dados
- Decisões arquiteturais do pipeline
- Apresentação final para entrega

---

### Github
Contém os arquivos de configuração para automação:

- Workflows do GitHub Actions
- Rotinas de agendamento diário

---

### Assets
Contém os arquivos locais e recursos visuais:

- `assets/`: Imagens da equipe e logotipos

---

### Arquivos Raiz
Documentos de configuração do repositório:

- `README.md`: Documentação principal explicando a estrutura e tecnologias
- `requirements.txt`: Dependências e bibliotecas Python
- `.gitignore`: Regras de exclusão de arquivos

---

## 🚫 Arquivos que NÃO ficam no repositório

Para manter organização e evitar conflitos, os seguintes arquivos não são versionados:

- Banco PostgreSQL / Credenciais (`.env`)
- Dados brutos do INPE, NASA e Copernicus
- Arquivos de ambientes virtuais (`venv`)
- Outputs gerados automaticamente
- Cache do Python

Esses arquivos são mantidos em pasta compartilhada do grupo ou gerenciados via secrets no GitHub.

---

## 🧱 Tecnologias Utilizadas

- Python (Pandas, Pingouin, Seaborn, Matplotlib, Requests e NumPy)
- PostgreSQL (Banco de Dados Online via Supabase)
- GitHub Actions (Orquestração e automação)
- Git e GitHub (Versionamento)

---

## 🔄 Fluxo de Atualização do Projeto

**1. Execução Automatizada:** Na madrugada de cada dia, a esteira de processamento é acionada de forma automática através do GitHub Actions.  

**2. Coleta e Análise de Dados:** Durante a execução, os scripts acessam as APIs da NASA, Copernicus e INPE, efetuam a extração, limpeza e cruzamento dos dados climáticos e espaciais.  

**3. Cálculo de Métricas e Banco de Dados:** Os limites matemáticos de anomalias (Score Z e IQR) são calculados e os dados consolidados atualizam o banco de dados PostgreSQL (hospedado no Supabase).  

**4. Consumo e Visualização:** O dashboard se conecta ao banco para consumir as tabelas, refletindo os resultados dos alertas diretamente na tela com carregamento otimizado.

---

## 📝 Observação

A validação do sistema não utiliza regras ou limiares arbitrários. Toda a lógica de alertas é embasada em métodos estatísticos robustos. A correlação entre as variáveis climáticas foi atestada matematicamente utilizando a Correlação de Spearman, garantindo o rigor científico da solução de monitoramento.

---

## 🔜 Próximos Passos

* Realizar mais análises a fim de melhorar o entendimento preditivo da dispersão das fumaças.
* Utilizar algoritmos de Machine Learning para análise preditiva com previsão da qualidade do ar.

---

Link para acesso à aplicação: <a href="#" target="_blank" rel="noopener noreferrer">Lorem Ipsum</a>

## 👥 Equipe

Projeto desenvolvido pela equipe Data Insight.

<table align="center" border="0" cellspacing="0" cellpadding="20">
  <tr>
    <td align="center" style="border:none;">
      <a href="https://github.com/DanielaPSilva">
        <img src="./assets/imagem-daniela.png" width="100px" style="border-radius:50%;" alt="Daniela Silva"/><br/>
        <b>Daniela Silva</b>
      </a>
    </td>
    <td align="center" style="border:none;">
      <a href="https://github.com/fabioamaralds">
        <img src="./assets/imagem-fabio.png" width="100px" style="border-radius:50%;" alt="Fabio Amaral"/><br/>
        <b>Fabio Amaral</b>
      </a>
    </td>
    <td align="center" style="border:none;">
      <a href="https://github.com/ReginaBolsanelli">
        <img src="./assets/imagem-regina.png" width="100px" style="border-radius:50%;" alt="Regina Bolsanelli"/><br/>
        <b>Regina Bolsanelli</b>
      </a>
    </td>
    <td align="center" style="border:none;">
      <a href="https://github.com/tilokao1">
        <img src="./assets/imagem-thiago.png" width="100px" style="border-radius:50%;" alt="Thiago Perez"/><br/>
        <b>Thiago Perez</b>
      </a>
    </td>
    <td align="center" style="border:none;">
      <a href="https://github.com/WagnerMartins-on">
        <img src="./assets/imagem-wagner.png" width="100px" style="border-radius:50%;" alt="Wagner Santana"/><br/>
        <b>Wagner Santana</b>
      </a>
    </td>
  </tr>
</table>