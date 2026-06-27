const { EmbedBuilder } = require('discord.js');

module.exports = {
    name: 'warn',
    description: 'Emite um aviso a um usuário',
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

        const warningEmbed = new EmbedBuilder()
            .setColor('#FFA500')
            .setTitle('Aviso Emitido')
            .setFields(
                { name: 'Usuário', value: `${user.username}`, inline: true },
                { name: 'Motivo', value: reason, inline: true },
                { name: 'Emitido por', value: message.author.username, inline: true }
            )
            .setFooter({ text: 'Chromo Bot - Sistema de Moderação' })
            .setTimestamp();

        await message.reply({ embeds: [warningEmbed] });

        try {
            const dmEmbed = new EmbedBuilder()
                .setColor('#FFA500')
                .setTitle('Você Recebeu um Aviso')
                .setDescription(`Servidor: ${message.guild.name}`)
                .setFields(
                    { name: 'Motivo', value: reason },
                    { name: 'Emitido por', value: message.author.username }
                )
                .setTimestamp();

            await user.send({ embeds: [dmEmbed] });
        } catch (err) {
            console.log('Não foi possível enviar DM para o usuário');
        }
    }
};
