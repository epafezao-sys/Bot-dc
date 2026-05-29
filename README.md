## 🤖 Bot Discord Profissional

Um bot Discord completo com funcionalidades avançadas de moderação, gerenciamento e segurança.

### 📋 Funcionalidades

#### 🛡️ Moderação
- **!kick** `@usuario [razão]` - Remover membro do servidor
- **!ban** `@usuario [razão]` - Banir membro permanentemente
- **!mute** `@usuario [minutos] [razão]` - Mutar membro por tempo determinado
- **!unmute** `@usuario` - Remover mute de um membro
- **!warn** `@usuario [razão]` - Avisar um membro (3 avisos = kick automático)
- **!warns** `@usuario` - Ver histórico de avisos
- **!clearwarn** `@usuario` - Limpar avisos

#### 📋 Informações
- **!info** `[@usuario]` - Ver informações de um membro
- **!serverinfo** - Ver informações do servidor
- **!avatar** `[@usuario]` - Ver avatar de um membro

#### ⭐ Sistema de Reputação
- **!rep** `@usuario` - Dar reputação (+1 ponto)
- **!reputation** `[@usuario]` - Verificar reputação
- **!top-reputation** - Top 10 membros mais reputados

#### 🎫 Sistema de Tickets
- **!ticket** - Criar um ticket privado
- **!closeticket** - Fechar ticket (apenas dentro do canal do ticket)

#### ⚙️ Configuração
- **!setlog** `#canal` - Configurar canal de logs
- **!setautorole** `@cargo` - Configurar autorole para novos membros
- **!addbannedword** `palavra` - Adicionar palavra proibida
- **!removebannedword** `palavra` - Remover palavra proibida
- **!listbannedwords** - Listar todas as palavras proibidas

### 🔒 Recursos de Segurança

1. **Proteção contra Spam**
   - Detecta quando um usuário envia mais de 5 mensagens em 10 segundos
   - Muta automaticamente por 5 minutos

2. **Proteção contra Raids**
   - Detecta quando mais de 10 membros entram em 1 minuto
   - Remove membros suspeitos automaticamente

3. **Filtro de Palavras Proibidas**
   - Configurável por servidor
   - Deleta mensagens automaticamente
   - Notifica o usuário via DM

4. **Sistema de Avisos**
   - Histórico completo de avisos
   - Kick automático após 3 avisos

5. **Logs Completos**
   - Registra todas as ações de moderação
   - Monitora entrada/saída de membros
   - Registra mensagens deletadas

### 📦 Instalação

#### Pré-requisitos
- Python 3.8+
- pip

#### Passos

1. **Clone o repositório:**
```bash
git clone https://github.com/epafezao-sys/Bot-dc-man.git
cd Bot-dc-man
```

2. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

3. **Configure o arquivo .env:**
```bash
cp .env.example .env
```

4. **Edite o arquivo `.env` e adicione seu token:**
```
DISCORD_TOKEN=seu_token_aqui
PREFIX=!
```

⚠️ **IMPORTANTE**: Nunca compartilhe seu token! Se fez isso, regenere imediatamente.

5. **Execute o bot:**
```bash
python bot.py
```

Você verá uma mensagem como:
```
✅ Bot conectado como NomeDoBotAqui#0000
🔧 Prefixo: !
```

### 🗂️ Estrutura

```
Bot-dc-man/
├── bot.py              # Código principal do bot
├── requirements.txt    # Dependências
├── .env.example        # Exemplo de variáveis de ambiente
├── .env                # Variáveis de ambiente (não fazer push)
├── .gitignore          # Arquivos a ignorar
├── bot_data.db        # Banco de dados (criado automaticamente)
└── README.md          # Este arquivo
```

### 📊 Banco de Dados

O bot usa SQLite para armazenar:
- **Avisos** de membros
- **Reputação** de usuários
- **Configurações** por servidor
- **Palavras proibidas**
- **Tickets**

### 🔑 Permissões Necessárias

Para funcionar corretamente, o bot precisa das seguintes permissões:

- ✅ Gerenciar mensagens
- ✅ Gerenciar membros
- ✅ Banir membros
- ✅ Remover membros
- ✅ Mutar membros
- ✅ Gerenciar canais
- ✅ Enviar mensagens
- ✅ Embutir links
- ✅ Ler histórico de mensagens

### 💡 Dicas de Uso

1. **Para um servidor novo:**
   - Configure um canal de logs: `!setlog #logs`
   - Configure autorole: `!setautorole @MeuCargoAqui`
   - Adicione palavras proibidas: `!addbannedword spam`

2. **Moderação:**
   - Use avisos antes de kicks: `!warn @usuario Spam`
   - Mantenha logs para documentação

3. **Reputação:**
   - Use `!rep @usuario` para reconhecer bom comportamento
   - Verifique o ranking: `!top-reputation`

### 🐛 Troubleshooting

**Bot não conecta:**
- Verifique o token no `.env`
- Certifique-se de que o token está válido (não foi regenerado)

**Comandos não funcionam:**
- Verifique permissões do bot
- Verifique se o bot tem o cargo no topo da hierarquia

**Logs não aparecem:**
- Execute `!setlog #canal` novamente
- Certifique-se de que o bot pode enviar mensagens no canal

### 📞 Suporte

Abra uma [issue](https://github.com/epafezao-sys/Bot-dc-man/issues) no repositório.

### 📄 Licença

MIT License - veja LICENSE para detalhes

---

**Desenvolvido com ❤️ para melhorar seu servidor Discord**
