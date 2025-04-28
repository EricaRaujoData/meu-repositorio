import pandas as pd

from datetime import datetime

# Lendo o arquivo Excel
BD_IA = pd.read_excel('C:\python\IA\BD_IA.xlsx')

# Ver todas as colunas
print(BD_IA.columns)

# Garante que a coluna seja do tipo datetime
BD_IA['GLICEMIA JEJUM'] = pd.to_datetime(BD_IA['GLICEMIA JEJUM'], errors='coerce')

# Cria a coluna SITUACAO com a diferença em dias
BD_IA['SITUACAO'] = (pd.to_datetime(datetime.today()) - BD_IA['GLICEMIA JEJUM']).dt.days

# Verificando a coluna criada no banco
print(BD_IA[['SITUACAO']].head())

# Salvando a coluna em um novo banco de dados
BD_IA.to_excel('BD_IA_atualizado.xlsx', index=False)

# Otimizando a query com todas as outras colunas de exames
exames = {
    'GLICEMIA JEJUM': 'SITUACAO_GLICEMIA',
    'HEMOGLOBINA GLICADA': 'SITUACAO_GLICADA',
    'CREATININA URINA': 'SITUACAO_CREATININA'
}

for exame, nome_coluna in exames.items():
    BD_IA[exame] = pd.to_datetime(BD_IA[exame], errors='coerce')
    BD_IA[nome_coluna] = (pd.to_datetime(datetime.today()) - BD_IA[exame]).dt.days
    
# Garante que as colunas de data estejam no formato datetime
exames = {
    'GLICEMIA JEJUM': 'SITUACAO_GLICEMIA',
    'HEMOGLOBINA GLICADA': 'SITUACAO_GLICADA',
    'CREATININA URINA': 'SITUACAO_CREATININA'
}

# Data atual
hoje = pd.to_datetime(datetime.today())

# Calcula a diferença em dias para cada exame
for exame, nome_coluna in exames.items():
    BD_IA[exame] = pd.to_datetime(BD_IA[exame], errors='coerce')  # Garante que os valores estão no formato datetime
    BD_IA[nome_coluna] = (hoje - BD_IA[exame]).dt.days  # Calcula a diferença em dias

# Salvando a coluna em um novo banco de dados
BD_IA.to_excel('BD_IA_atualizado_3.xlsx', index=False)


# Parâmetros de dias para considerar atraso
parametros = {
    'GLICEMIA JEJUM': ('SITUACAO_GLICEMIA', 'STATUS_GLICEMIA', 30),
    'HEMOGLOBINA GLICADA': ('SITUACAO_GLICADA', 'STATUS_GLICADA', 180),
    'CREATININA URINA': ('SITUACAO_CREATININA', 'STATUS_CREATININA', 365)
}

# Data de referência
hoje = pd.to_datetime(datetime.today())

# Calcula os dias e o status
for exame, (coluna_dias, coluna_status, limite) in parametros.items():
    BD_IA[exame] = pd.to_datetime(BD_IA[exame], errors='coerce')
    BD_IA[coluna_dias] = (hoje - BD_IA[exame]).dt.days
    BD_IA[coluna_status] = BD_IA[coluna_dias].apply(
        lambda x: 'atrasado' if pd.notnull(x) and x > limite else 'em dia'
    )
    
    
    # Salvando a coluna em um novo banco de dados
BD_IA.to_excel('BD_IA_atualizado_4.xlsx', index=False)

##############################

# Criando API para guardar o código

from fastapi import FastAPI, UploadFile, File
import pandas as pd
from datetime import datetime
from io import BytesIO

app = FastAPI()

@app.post("/processar-exames/")
async def processar_exames(file: UploadFile = File(...)):
    # Lê o Excel enviado
    contents = await file.read()
    BD_IA = pd.read_excel(BytesIO(contents))
    
 # Define os exames, nomes das colunas e limites
    exames = {
        'GLICEMIA JEJUM': ('SITUACAO_GLICEMIA', 30),
        'HEMOGLOBINA GLICADA': ('SITUACAO_GLICADA', 180),
        'CREATININA URINA': ('SITUACAO_CREATININA', 365)
    }

    hoje = pd.to_datetime(datetime.today())

    for exame, (coluna_base, limite) in exames.items():
        BD_IA[exame] = pd.to_datetime(BD_IA[exame], errors='coerce')
        dias_col = f'{coluna_base}_DIAS'
        BD_IA[dias_col] = (hoje - BD_IA[exame]).dt.days
        BD_IA[coluna_base] = BD_IA[dias_col].apply(
            lambda x: 'EM DIA' if pd.notnull(x) and x <= limite else 'ATRASADO'
        )

    # Retorna as primeiras 5 linhas com as novas colunas
    return BD_IA.head().to_dict(orient="records")

import uvicorn

if __name__ == '__main__':
    uvicorn.run("api_exames:app", host="127.0.0.1", port=8000, reload=True)
