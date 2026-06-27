const { EmbedBuilder } = require('discord.js');

module.exports = {
    name: 'stats',
    description: 'Mostra estatísticas do servidor',
    execute: async (message, client) => {
        const guild = message.guild;
        const totalMembers = guild.memberCount;
        const botMembers = guild.members.cache.filter(m => m.user.bot).size;
        const humanMembers = totalMembers - botMembers;
        const channels = guild.channels.cache.size;
        const roles = guild.roles.cache.size;

        const embed = new EmbedBuilder()
            .setColor('#5865F2')
            .setTitle('Estatísticas do Servidor')
            .setThumbnail(guild.iconURL())
            .setFields(
                { name: 'Nome do Servidor', value: guild.name, inline: true },
                { name: 'ID do Servidor', value: guild.id, inline: true },
                { name: 'Criado em', value: `<t:${Math.floor(guild.createdTimestamp / 1000)}:d>`, inline: true },
                { name: 'Total de Membros', value: totalMembers.toString(), inline: true },
                { name: 'Membros Humanos', value: humanMembers.toString(), inline: true },
                { name: 'Bots', value: botMembers.toString(), inline: true },
                { name: 'Canais', value: channels.toString(), inline: true },
                { name: 'Funções', value: roles.toString(), inline: true },
                { name: 'Dono', value: `<@${guild.ownerId}>`, inline: true }
            )
            .setFooter({ text: 'Chromo Bot - Estatísticas' })
            .setTimestamp();

        await message.reply({ embeds: [embed] });
    }
};
