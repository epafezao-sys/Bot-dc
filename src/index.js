require('dotenv').config();
const { Client, GatewayIntentBits, EmbedBuilder, ActionRowBuilder, ButtonBuilder, ButtonStyle } = require('discord.js');
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
            .setTitle('Erro na Execução')
            .setDescription('Ocorreu um erro ao processar seu comando.')
            .setFooter({ text: 'Chromo Bot' })
            .setTimestamp();

        await message.reply({ embeds: [errorEmbed] }).catch(err => console.error(err));
    }
});

// Sistema de Interações - Botões
client.on('interactionCreate', async interaction => {
    try {
        if (interaction.isButton()) {
            const customId = interaction.customId;

            if (customId === 'create_ticket') {
                const ticketEmbed = new EmbedBuilder()
                    .setColor('#5865F2')
                    .setTitle('Novo Ticket Criado')
                    .setDescription(`Ticket criado por ${interaction.user.username}`)
                    .setFields(
                        { name: 'ID', value: `ticket-${Date.now()}`, inline: true },
                        { name: 'Status', value: 'Aberto', inline: true }
                    )
                    .setFooter({ text: 'Chromo Bot - Tickets' })
                    .setTimestamp();

                await interaction.reply({ embeds: [ticketEmbed] });
            } else if (customId === 'close_ticket') {
                const closeEmbed = new EmbedBuilder()
                    .setColor('#FF6B6B')
                    .setTitle('Ticket Fechado')
                    .setDescription(`Ticket fechado por ${interaction.user.username}`)
                    .setFooter({ text: 'Chromo Bot - Tickets' })
                    .setTimestamp();

                await interaction.reply({ embeds: [closeEmbed] });
            }
        }

        // Sistema de Interações - Menus Selecionáveis
        if (interaction.isStringSelectMenu()) {
            if (interaction.customId === 'help_menu') {
                let helpText = '';
                
                if (interaction.values[0] === 'gerais') {
                    helpText = `
**Comandos Gerais:**
• !ping - Mostra a latência do bot
• !info - Informações do bot
• !stats - Estatísticas do servidor
• !userinfo @usuario - Info do usuário
                    `;
                } else if (interaction.values[0] === 'tickets') {
                    helpText = `
**Sistema de Tickets:**
• !ticket - Abre o menu de tickets
Use os botões para criar ou fechar tickets
                    `;
                } else if (interaction.values[0] === 'moderacao') {
                    helpText = `
**Comandos de Moderação:**
• !warn @usuario motivo - Avisar usuário
• !mute @usuario motivo - Silenciar usuário
• !kick @usuario motivo - Expulsar usuário
• !ban @usuario motivo - Banir usuário
                    `;
                }

                const embed = new EmbedBuilder()
                    .setColor('#5865F2')
                    .setTitle('Central de Ajuda')
                    .setDescription(helpText)
                    .setFooter({ text: 'Chromo Bot' })
                    .setTimestamp();

                await interaction.reply({ embeds: [embed] });
            }
        }
    } catch (error) {
        console.error('Erro na interação:', error);
        
        if (!interaction.replied) {
            await interaction.reply({ 
                content: 'Ocorreu um erro ao processar sua interação.',
                ephemeral: true 
            }).catch(err => console.error(err));
        }
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
