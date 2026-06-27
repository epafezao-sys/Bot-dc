const { EmbedBuilder } = require('discord.js');

module.exports = {
    name: 'ping',
    description: 'Verifica a latência do bot',
    execute: async (message, client) => {
        const embed = new EmbedBuilder()
            .setColor('#2F3136')
            .setTitle('⚡ Status de Conexão')
            .setDescription('Verificando latência...')
            .setFooter({ text: 'Chromo Bot', iconURL: client.user.avatarURL() })
            .setTimestamp();

        const msg = await message.reply({ embeds: [embed] });
        
        const latency = msg.createdTimestamp - message.createdTimestamp;
        const apiLatency = Math.round(client.ws.ping);

        embed
            .setDescription(`✅ Conexão estável`)
            .setFields(
                { name: '🔌 Latência do Bot', value: `${latency}ms`, inline: true },
                { name: '📡 Latência da API', value: `${apiLatency}ms`, inline: true }
            )
            .setColor('#5865F2');

        await msg.edit({ embeds: [embed] });
    }
};