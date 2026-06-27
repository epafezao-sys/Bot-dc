const { EmbedBuilder, ActionRowBuilder, ButtonBuilder, ButtonStyle } = require('discord.js');

module.exports = {
    name: 'ticket',
    description: 'Sistema de tickets',
    execute: async (message, client) => {
        const embed = new EmbedBuilder()
            .setColor('#5865F2')
            .setTitle('Sistema de Tickets')
            .setDescription('Clique no botão abaixo para criar um ticket de suporte')
            .setFields(
                { name: 'Problemas com Executor', value: 'Reporte problemas técnicos', inline: true },
                { name: 'Suporte', value: 'Solicite ajuda', inline: true },
                { name: 'Denúncia', value: 'Reporte usuários', inline: true }
            )
            .setFooter({ text: 'Chromo Bot - Sistema de Tickets' })
            .setTimestamp();

        const row = new ActionRowBuilder()
            .addComponents(
                new ButtonBuilder()
                    .setCustomId('create_ticket')
                    .setLabel('Criar Ticket')
                    .setStyle(ButtonStyle.Primary),
                new ButtonBuilder()
                    .setCustomId('close_ticket')
                    .setLabel('Fechar Ticket')
                    .setStyle(ButtonStyle.Danger)
            );

        await message.reply({ embeds: [embed], components: [row] });
    }
};
