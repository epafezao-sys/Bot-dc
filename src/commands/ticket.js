const { EmbedBuilder, ActionRowBuilder, ButtonBuilder, ButtonStyle, ModalBuilder, TextInputBuilder, TextInputStyle, ChannelType } = require('discord.js');

module.exports = {
    name: 'ticket',
    description: 'Sistema profissional de tickets',
    execute: async (message, client) => {
        // Verificar se o usuário é admin
        if (!message.member.permissions.has('Administrator')) {
            const errorEmbed = new EmbedBuilder()
                .setColor('#FF0000')
                .setTitle('Acesso Negado')
                .setDescription('Apenas administradores podem usar este comando.');
            return await message.reply({ embeds: [errorEmbed] });
        }

        // Criar modal de configuração
        const modal = new ModalBuilder()
            .setCustomId('ticket_setup_modal')
            .setTitle('Configurar Sistema de Tickets');

        const titleInput = new TextInputBuilder()
            .setCustomId('ticket_title')
            .setLabel('Título do Painel de Tickets')
            .setStyle(TextInputStyle.Short)
            .setPlaceholder('Ex: Sistema de Suporte')
            .setRequired(true);

        const descriptionInput = new TextInputBuilder()
            .setCustomId('ticket_description')
            .setLabel('Descrição do Painel')
            .setStyle(TextInputStyle.Paragraph)
            .setPlaceholder('Ex: Clique em um botão abaixo para criar um ticket')
            .setRequired(true);

        const channelInput = new TextInputBuilder()
            .setCustomId('ticket_channel')
            .setLabel('ID do Canal para Tickets')
            .setStyle(TextInputStyle.Short)
            .setPlaceholder('Ex: 123456789')
            .setRequired(true);

        const firstActionRow = new ActionRowBuilder().addComponents(titleInput);
        const secondActionRow = new ActionRowBuilder().addComponents(descriptionInput);
        const thirdActionRow = new ActionRowBuilder().addComponents(channelInput);

        modal.addComponents(firstActionRow, secondActionRow, thirdActionRow);

        await message.showModal(modal);
    }
};
