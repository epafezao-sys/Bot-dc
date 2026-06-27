# ⚡ Chromo Bot - Discord Premium

Bot oficial do servidor do Executor com design profissional e funcionalidades avançadas.

## 📋 Requisitos

- Node.js 18.x ou superior
- NPM ou Yarn
- Discord Bot Token

## 🚀 Instalação Local

### 1. Clone o repositório
```bash
git clone https://github.com/epafezao-sys/Bot-dc.git
cd Bot-dc
```

### 2. Instale as dependências
```bash
npm install
```

### 3. Configure o arquivo `.env`
```env
DISCORD_TOKEN=seu_token_aqui
PORT=3000
```

### 4. Execute o bot
```bash
npm start
```

Para desenvolvimento com auto-reload:
```bash
npm run dev
```

## 🌐 Deploy no Render

### Passo 1: Configure o Render
1. Acesse [render.com](https://render.com)
2. Crie uma conta e faça login
3. Clique em **"New +'** → **"Web Service"**
4. Conecte seu repositório GitHub

### Passo 2: Configurações do Deploy

**Tipo de Serviço:** `Web Service`

**Build Command:**
```bash
npm install
```

**Start Command:**
```bash
npm start
```

**Plano:** Free (ou Pro se desejar uptime 100%)

### Passo 3: Adicione as Variáveis de Ambiente
No painel do Render, vá para **"Environment"** e adicione:

| Chave | Valor |
|-------|-------|
| `DISCORD_TOKEN` | Seu token do bot (obtém em Discord Developer Portal) |
| `PORT` | 3000 |
| `NODE_ENV` | production |

### Passo 4: Deploy
Clique em **"Create Web Service"** e o Render começará o deploy automaticamente.

## 📝 Comandos Disponíveis

### `!ping`
Verifica a latência e status de conexão do bot.

### `!info`
Mostra informações detalhadas sobre o bot (uptime, servidores, ping, etc).

## 🎨 Design & Estética

- **Cores:** Azul Discord (#5865F2) e Cinza Premium (#2F3136)
- **Emojis:** ⚡ ⚙️ 🛡️ 🌐 📊 🟢 (profissionais e modernos)
- **Embeds:** Todas as respostas usam MessageEmbeds para consistência visual
- **Footer:** Marca "Chromo Bot" em todas as mensagens

## 🔧 Estrutura de Pastas

```
Bot-dc/
├── src/
│   ├── index.js           # Bot principal
│   ├── server.js          # Servidor Express (Keep-Alive)
│   └── commands/          # Comandos modulares
│       ├── ping.js
│       └── info.js
├── .env.example           # Template de variáveis
├── .gitignore             # Arquivos a ignorar
├── package.json           # Dependências
└── README.md              # Este arquivo
```

## 🛡️ Segurança

- ✅ Token nunca fica no repositório (usa `.env`)
- ✅ `.env` está no `.gitignore`
- ✅ Tratamento de erros implementado
- ✅ Validação de permissões possível (extensível)

## 📡 Tecnologias

- **Discord.js v14** - API do Discord
- **Express.js** - Servidor web para Keep-Alive no Render
- **dotenv** - Gerenciamento de variáveis

## 🚨 Troubleshooting

### Bot não sobe no Render
- Verifique se o `DISCORD_TOKEN` está correto no painel
- Confira se o Build Command é `npm install`
- Verifique os logs no Render

### Comando não funciona
- Certifique-se que o comando começa com `!`
- Confirme se o arquivo está em `src/commands/`
- Reinicie o bot

## 📞 Como Adicionar Novos Comandos

Crie um arquivo em `src/commands/seu-comando.js`:

```javascript
const { EmbedBuilder } = require('discord.js');

module.exports = {
    name: 'seu-comando',
    description: 'Descrição do comando',
    execute: async (message, client) => {
        const embed = new EmbedBuilder()
            .setColor('#5865F2')
            .setTitle('Título')
            .setDescription('Sua resposta aqui')
            .setFooter({ text: 'Chromo Bot' })
            .setTimestamp();

        await message.reply({ embeds: [embed] });
    }
};
```

---

**Desenvolvido com ⚡ para a comunidade do Executor**