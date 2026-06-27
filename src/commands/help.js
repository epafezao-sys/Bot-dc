const { EmbedBuilder, ActionRowBuilder, StringSelectMenuBuilder } = require('discord.js');

module.exports = {
    name: 'help',
    description: 'Mostra todos os comandos disponíveis',
    execute: async (message, client) => {
        const embed = new EmbedBuilder()
            .setColor('#5865F2')
            .setTitle('Central de Ajuda')
            .setDescription('Selecione uma categoria para ver os comandos')
            .setFields(
                { name: 'Comandos Gerais', value: '!ping, !info, !help', inline: false },
                { name: 'Sistema de Tickets', value: '!ticket', inline: false },
                { name: 'Estatísticas', value: '!stats', inline: false },
                { name: 'Moderação', value: '!warn, !mute, !kick', inline: false }
            )
            .setFooter({ text: 'Use !help <comando> para mais informações' })
            .setTimestamp();

        const row = new ActionRowBuilder()
            .addComponents(
                new StringSelectMenuBuilder()
                    .setCustomId('help_menu')
                    .setPlaceholder('Selecione uma categoria')
                    .addOptions(
                        { label: 'Gerais', value: 'gerais' },
                        { label: 'Tickets', value: 'tickets' },
                        { label: 'Moderação', value: 'moderacao' }
                    )
            );

        await message.reply({ embeds: [embed], components: [row] });
    }
};
