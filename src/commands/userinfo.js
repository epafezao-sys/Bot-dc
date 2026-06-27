const { EmbedBuilder } = require('discord.js');

module.exports = {
    name: 'userinfo',
    description: 'Mostra informações de um usuário',
    execute: async (message, client) => {
        const user = message.mentions.users.first() || message.author;
        const member = await message.guild.members.fetch(user.id);

        const roles = member.roles.cache.filter(r => r.id !== message.guild.id).map(r => r.toString()).join(', ') || 'Nenhuma';
        const joinedAt = Math.floor(member.joinedTimestamp / 1000);
        const createdAt = Math.floor(user.createdTimestamp / 1000);

        const embed = new EmbedBuilder()
            .setColor('#5865F2')
            .setTitle(`Informações de ${user.username}`)
            .setThumbnail(user.avatarURL())
            .setFields(
                { name: 'Nome de Usuário', value: user.username, inline: true },
                { name: 'ID', value: user.id, inline: true },
                { name: 'Bot', value: user.bot ? 'Sim' : 'Não', inline: true },
                { name: 'Entrou no Servidor', value: `<t:${joinedAt}:d>`, inline: true },
                { name: 'Conta Criada em', value: `<t:${createdAt}:d>`, inline: true },
                { name: 'Status', value: member.presence?.status || 'offline', inline: true },
                { name: 'Funções', value: roles }
            )
            .setFooter({ text: 'Chromo Bot - Informações de Usuário' })
            .setTimestamp();

        await message.reply({ embeds: [embed] });
    }
};
