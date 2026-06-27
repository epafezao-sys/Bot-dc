require('dotenv').config();
const { Client, GatewayIntentBits, EmbedBuilder } = require('discord.js');
const keepAlive = require('./server');
const fs = require('fs');
const path = require('path');

const client = new Client({
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.MessageContent,
        GatewayIntentBits.DirectMessages
    ]
});

// Carrega os comandos
const commands = {};
const commandsPath = path.join(__dirname, 'commands');
const commandFiles = fs.readdirSync(commandsPath).filter(file => file.endsWith('.js'));

for (const file of commandFiles) {
    const filePath = path.join(commandsPath, file);
    const command = require(filePath);
    commands[command.name] = command;
}

client.once('ready', () => {
    console.log(`\n✅ ========================================`);
    console.log(`🤖 Chromo está ONLINE!`);
    console.log(`📊 Logado como: ${client.user.tag}`);
    console.log(`========================================\n`);
    
    client.user.setActivity('⚡ Protegendo o servidor', { type: 'WATCHING' });
});

client.on('messageCreate', async message => {
    // Ignora mensagens de bots
    if (message.author.bot) return;

    // Processa apenas mensagens que começam com !
    if (!message.content.startsWith('!')) return;

    const args = message.content.slice(1).toLowerCase().split(/\s+/);
    const commandName = args[0];

    if (!commands[commandName]) return;

    try {
        await commands[commandName].execute(message, client);
    } catch (error) {
        console.error(`❌ Erro ao executar comando ${commandName}:`, error);
        
        const errorEmbed = new EmbedBuilder()
            .setColor('#FF0000')
            .setTitle('⚠️ Erro na Execução')
            .setDescription('Ocorreu um erro ao processar seu comando.')
            .setFooter({ text: 'Chromo Bot' })
            .setTimestamp();

        await message.reply({ embeds: [errorEmbed] }).catch(err => console.error(err));
    }
});

client.on('guildCreate', guild => {
    console.log(`✨ Chromo adicionado ao servidor: ${guild.name} (${guild.id})`);
});

client.on('guildDelete', guild => {
    console.log(`⚠️ Chromo removido do servidor: ${guild.name} (${guild.id})`);
});

// Inicia o servidor web para o Render não derrubar a aplicação
keepAlive();

// Conecta o bot
client.login(process.env.DISCORD_TOKEN);
