const { EmbedBuilder } = require('discord.js');

module.exports = {
    name: 'mute',
    description: 'Silencia um usuário',
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

        const member = await message.guild.members.fetch(user.id).catch(() => null);

        if (!member) {
            const errorEmbed = new EmbedBuilder()
                .setColor('#FF0000')
                .setTitle('Erro')
                .setDescription('Usuário não encontrado no servidor');
            return await message.reply({ embeds: [errorEmbed] });
        }

        const muteRole = message.guild.roles.cache.find(r => r.name === 'Mutado');

        if (!muteRole) {
            const errorEmbed = new EmbedBuilder()
                .setColor('#FF0000')
                .setTitle('Erro')
                .setDescription('Role "Mutado" não encontrada. Crie uma role com este nome');
            return await message.reply({ embeds: [errorEmbed] });
        }

        try {
            await member.roles.add(muteRole);

            const muteEmbed = new EmbedBuilder()
                .setColor('#5865F2')
                .setTitle('Usuário Silenciado')
                .setFields(
                    { name: 'Usuário', value: user.username, inline: true },
                    { name: 'Motivo', value: reason, inline: true },
                    { name: 'Emitido por', value: message.author.username, inline: true }
                )
                .setFooter({ text: 'Chromo Bot - Sistema de Moderação' })
                .setTimestamp();

            await message.reply({ embeds: [muteEmbed] });
        } catch (err) {
            const errorEmbed = new EmbedBuilder()
                .setColor('#FF0000')
                .setTitle('Erro')
                .setDescription('Não foi possível silenciar o usuário');
            await message.reply({ embeds: [errorEmbed] });
        }
    }
};
