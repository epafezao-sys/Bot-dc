const { EmbedBuilder } = require('discord.js');

module.exports = {
    name: 'kick',
    description: 'Expulsa um usuário do servidor',
    execute: async (message, client) => {
        // Verificar se o usuário é admin
        if (!message.member.permissions.has('Administrator')) {
            const errorEmbed = new EmbedBuilder()
                .setColor('#FF0000')
                .setTitle('Acesso Negado')
                .setDescription('Apenas administradores podem usar este comando.');
            return await message.reply({ embeds: [errorEmbed] });
        }

        const user = message.mentions.users.first();
        const reason = message.content.split(' ').slice(2).join(' ') || 'Motivo não especificado';

        if (!user) {
            const errorEmbed = new EmbedBuilder()
                .setColor('#FF0000')
                .setTitle('Erro')
                .setDescription('Você precisa mencionar um usuário');
            return await message.reply({ embeds: [errorEmbed] });
        }

        const member = await message.guild.members.fetch(user.id).catch(() => null);

        if (!member) {
            const errorEmbed = new EmbedBuilder()
                .setColor('#FF0000')
                .setTitle('Erro')
                .setDescription('Usuário não encontrado no servidor');
            return await message.reply({ embeds: [errorEmbed] });
        }

        try {
            await member.kick(reason);

            const kickEmbed = new EmbedBuilder()
                .setColor('#FF6B6B')
                .setTitle('Usuário Expulso')
                .setFields(
                    { name: 'Usuário', value: user.username, inline: true },
                    { name: 'Motivo', value: reason, inline: true },
                    { name: 'Emitido por', value: message.author.username, inline: true }
                )
                .setFooter({ text: 'Chromo Bot - Sistema de Moderação' })
                .setTimestamp();

            await message.reply({ embeds: [kickEmbed] });
        } catch (err) {
            const errorEmbed = new EmbedBuilder()
                .setColor('#FF0000')
                .setTitle('Erro')
                .setDescription('Não foi possível expulsar o usuário');
            await message.reply({ embeds: [errorEmbed] });
        }
    }
};
