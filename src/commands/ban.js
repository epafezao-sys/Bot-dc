const { EmbedBuilder } = require('discord.js');

module.exports = {
    name: 'ban',
    description: 'Banir um usuário do servidor',
    execute: async (message, client) => {
        const user = message.mentions.users.first();
        const reason = message.content.split(' ').slice(2).join(' ') || 'Motivo não especificado';

        if (!user) {
            const errorEmbed = new EmbedBuilder()
                .setColor('#FF0000')
                .setTitle('Erro')
                .setDescription('Você precisa mencionar um usuário');
            return await message.reply({ embeds: [errorEmbed] });
        }

        try {
            await message.guild.members.ban(user, { reason });

            const banEmbed = new EmbedBuilder()
                .setColor('#8B0000')
                .setTitle('Usuário Banido')
                .setFields(
                    { name: 'Usuário', value: user.username, inline: true },
                    { name: 'Motivo', value: reason, inline: true },
                    { name: 'Emitido por', value: message.author.username, inline: true }
                )
                .setFooter({ text: 'Chromo Bot - Sistema de Moderação' })
                .setTimestamp();

            await message.reply({ embeds: [banEmbed] });
        } catch (err) {
            const errorEmbed = new EmbedBuilder()
                .setColor('#FF0000')
                .setTitle('Erro')
                .setDescription('Não foi possível banir o usuário');
            await message.reply({ embeds: [errorEmbed] });
        }
    }
};
