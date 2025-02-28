# Plataforma de Fitness e Dietas

Uma plataforma web desenvolvida com Django para ajudar usuários a calcular suas necessidades calóricas e receber sugestões de dietas personalizadas usando Inteligência Artificial.

## Funcionalidades Implementadas

- Registro e autenticação de usuários
- Cálculo de Taxa Metabólica Basal (BMR) e Gasto Energético Total Diário (TDEE)
- Cálculo de macronutrientes personalizados
- Sugestão de plano de refeições diário usando IA
- Dashboard interativo com gráficos
- Interface responsiva com Bootstrap 5
- Sistema de feedback de dietas
- Gerenciamento de alimentos personalizados (preferências e restrições)
- API REST com autenticação por chave
- Painel administrativo para gerenciamento de IA

## Estrutura do Projeto

```
fitness_platform/
├── core/                      # Aplicativo principal
│   ├── management/           # Comandos personalizados do Django
│   │   └── commands/
│   │       └── populate_alimentos.py
│   │       └── train_diet_model.py
│   ├── migrations/          # Migrações do banco de dados
│   ├── ml_models/          # Modelos de IA
│   │   ├── diet_model.py
│   │   └── utils.py
│   ├── templates/          # Templates HTML
│   ├── templatetags/       # Tags personalizadas
│   ├── admin.py           # Configuração do admin
│   ├── forms.py           # Formulários
│   ├── models.py          # Modelos do banco de dados
│   ├── views.py           # Views principais
│   ├── views_admin.py     # Views do painel admin
│   └── views_api.py       # Views da API
└── fitness_platform/        # Configurações do projeto
    ├── settings.py
    └── urls.py
```

## Requisitos

- Python 3.8 ou superior
- MySQL 5.7 ou superior
- Mínimo de 8GB de RAM recomendado
- Espaço em disco: mínimo 10GB livre

## Dependências Principais

- Django==5.0.6
- mysqlclient==2.2.7
- PyTorch (CPU ou CUDA)
- scikit-learn==1.4.0
- numpy==1.26.4
- pandas==2.2.0
- transformers==4.37.2
- python-dotenv==1.0.1

## Instalação

1. Clone o repositório:
```bash
git clone https://seu-repositorio/fitness-platform.git
cd fitness-platform
```

2. Crie e ative um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Instale o PyTorch (escolha uma opção):

Para versão CPU (recomendado para desenvolvimento):
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

Para versão CUDA (se tiver GPU NVIDIA):
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

5. Configure o banco de dados MySQL:
- Crie um banco de dados chamado `fitness_db`
- Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:
```
DB_NAME=fitness_db
DB_USER=seu_usuario
DB_PASSWORD=sua_senha
DB_HOST=localhost
DB_PORT=3306
SECRET_KEY=sua_chave_secreta
```

6. Execute as migrações:
```bash
python manage.py makemigrations
python manage.py migrate
```

7. Popule o banco de dados com alimentos iniciais:
```bash
python manage.py populate_alimentos
```

8. Crie um superusuário:
```bash
python manage.py createsuperuser
```

9. Treine o modelo de IA (opcional neste momento):
```bash
python manage.py train_diet_model
```

10. Inicie o servidor de desenvolvimento:
```bash
python manage.py runserver
```

## Uso

1. Acesse `http://localhost:8000` no seu navegador
2. Crie uma conta ou faça login
3. Complete seu perfil de saúde
4. Visualize seu dashboard com informações personalizadas e sugestões de dieta

## Administração

- Acesse `http://localhost:8000/admin` para gerenciar:
  - Usuários e perfis
  - Alimentos e dietas
  - Configurações de IA
  - Documentos de treinamento
  - Chaves de API

## API REST

A API possui os seguintes endpoints:

- `/api/status/` - Verifica o status da API
- `/api/modelos/` - Lista modelos de IA disponíveis
- `/api/documentos/` - Lista documentos de treinamento (requer acesso especial)

Autenticação via header `X-API-Key`

## Estado Atual do Projeto

- [x] Estrutura básica do projeto
- [x] Modelos de dados
- [x] Sistema de autenticação
- [x] Interface administrativa
- [x] API REST
- [x] Testes da API
- [ ] Treinamento do modelo de IA (pendente)
- [ ] Deploy em produção

## Próximos Passos

1. Resolver problemas de memória no treinamento do modelo
2. Implementar mais testes unitários
3. Melhorar a documentação da API
4. Adicionar mais métricas no dashboard
5. Implementar sistema de pagamentos

## Contribuição

Contribuições são bem-vindas! Por favor, sinta-se à vontade para enviar pull requests.

## Licença

Este projeto está sob a licença MIT. 