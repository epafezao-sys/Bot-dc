const { EmbedBuilder } = require('discord.js');

module.exports = {
    name: 'info',
    description: 'Mostra informações do bot',
    execute: async (message, client) => {
        const uptime = Math.floor(client.uptime / 1000);
        const uptimeFormatted = `${Math.floor(uptime / 3600)}h ${Math.floor((uptime % 3600) / 60)}m`;

        const embed = new EmbedBuilder()
            .setColor('#5865F2')
            .setTitle('⚙️ Informações do Chromo')
            .setThumbnail(client.user.avatarURL())
            .setDescription('Bot premium para gerenciamento e proteção')
            .setFields(
                { name: '🤖 Nome', value: client.user.username, inline: true },
                { name: '📊 Versão', value: '1.0.0', inline: true },
                { name: '⏱️ Uptime', value: uptimeFormatted, inline: true },
                { name: '🌐 Servidores', value: client.guilds.cache.size.toString(), inline: true },
                { name: '👥 Usuários', value: client.users.cache.size.toString(), inline: true },
                { name: '📡 Ping', value: `${Math.round(client.ws.ping)}ms`, inline: true }
            )
            .setFooter({ text: 'Chromo Bot © 2024', iconURL: client.user.avatarURL() })
            .setTimestamp();

        await message.reply({ embeds: [embed] });
    }
};