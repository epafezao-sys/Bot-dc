import discord
from discord.ext import commands, tasks
import os
from dotenv import load_dotenv
import sqlite3
from datetime import datetime, timedelta
import asyncio
from collections import defaultdict

# Carregar variáveis de ambiente
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
PREFIX = os.getenv('PREFIX', '!')

# Configurar intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.moderation = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

# ============================================
# BANCO DE DADOS
# ============================================

def init_database():
    """Inicializar banco de dados"""
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    
    # Tabela de avisos
    cursor.execute('''CREATE TABLE IF NOT EXISTS warns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        guild_id INTEGER,
        moderator_id INTEGER,
        reason TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Tabela de reputação
    cursor.execute('''CREATE TABLE IF NOT EXISTS reputation (
        user_id INTEGER PRIMARY KEY,
        guild_id INTEGER,
        points INTEGER DEFAULT 0,
        UNIQUE(user_id, guild_id)
    )''')
    
    # Tabela de configurações
    cursor.execute('''CREATE TABLE IF NOT EXISTS config (
        guild_id INTEGER PRIMARY KEY,
        log_channel_id INTEGER,
        mod_role_id INTEGER,
        autorole_id INTEGER,
        spam_threshold INTEGER DEFAULT 5,
        spam_timeout INTEGER DEFAULT 60
    )''')
    
    # Tabela de palavras proibidas
    cursor.execute('''CREATE TABLE IF NOT EXISTS banned_words (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        guild_id INTEGER,
        word TEXT
    )''')
    
    # Tabela de tickets
    cursor.execute('''CREATE TABLE IF NOT EXISTS tickets (
        ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
        guild_id INTEGER,
        user_id INTEGER,
        channel_id INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        closed INTEGER DEFAULT 0
    )''')
    
    conn.commit()
    conn.close()

# ============================================
# VARIÁVEIS GLOBAIS
# ============================================

spam_tracking = defaultdict(lambda: {'count': 0, 'first_message': None})
raid_protection = defaultdict(lambda: {'count': 0, 'timeout': None})

# ============================================
# EVENTOS
# ============================================

@bot.event
async def on_ready():
    """Bot conectado com sucesso"""
    print(f'✅ Bot conectado como {bot.user}')
    print(f'🔧 Prefixo: {PREFIX}')
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching,
        name=f"seu servidor | {PREFIX}help"
    ))
    init_database()
    check_spam.start()

@bot.event
async def on_member_join(member):
    """Novo membro entrou no servidor"""
    guild = member.guild
    
    # Dar autorole se configurado
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT autorole_id FROM config WHERE guild_id = ?', (guild.id,))
    result = cursor.fetchone()
    conn.close()
    
    if result and result[0]:
        try:
            role = guild.get_role(result[0])
            if role:
                await member.add_roles(role)
        except:
            pass
    
    # Log
    await log_action(guild, f"👤 Novo membro: {member.mention} ({member.id})")
    
    # Proteção contra raids
    await check_raid_protection(guild, member)

@bot.event
async def on_message(message):
    """Mensagem enviada"""
    if message.author.bot:
        return
    
    # Verificar spam
    await check_spam_message(message)
    
    # Verificar palavras proibidas
    await check_banned_words(message)
    
    await bot.process_commands(message)

@bot.event
async def on_message_delete(message):
    """Mensagem deletada"""
    if message.author.bot:
        return
    await log_action(message.guild, f"🗑️ Mensagem deletada de {message.author.mention}: {message.content[:50]}")

@bot.event
async def on_member_remove(member):
    """Membro saiu do servidor"""
    await log_action(member.guild, f"👋 Membro saiu: {member.mention} ({member.id})")

# ============================================
# FUNÇÕES DE PROTEÇÃO
# ============================================

async def log_action(guild, action):
    """Log de ações no servidor"""
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT log_channel_id FROM config WHERE guild_id = ?', (guild.id,))
    result = cursor.fetchone()
    conn.close()
    
    if result and result[0]:
        try:
            channel = guild.get_channel(result[0])
            if channel:
                embed = discord.Embed(
                    description=action,
                    color=discord.Color.blue(),
                    timestamp=datetime.now()
                )
                await channel.send(embed=embed)
        except:
            pass

async def check_spam_message(message):
    """Verificar spam de mensagens"""
    user_id = message.author.id
    current_time = datetime.now()
    
    user_data = spam_tracking[user_id]
    
    if user_data['first_message'] is None:
        user_data['first_message'] = current_time
        user_data['count'] = 1
    else:
        time_diff = (current_time - user_data['first_message']).total_seconds()
        
        if time_diff < 10:  # 10 segundos
            user_data['count'] += 1
            
            if user_data['count'] > 5:  # Mais de 5 mensagens em 10 segundos
                try:
                    await message.author.timeout(timedelta(minutes=5), reason="Spam detectado")
                    await log_action(message.guild, f"⏸️ {message.author.mention} foi mutado por spam (5 mensagens em 10s)")
                    spam_tracking[user_id] = {'count': 0, 'first_message': None}
                except:
                    pass
        else:
            user_data['first_message'] = current_time
            user_data['count'] = 1

async def check_banned_words(message):
    """Verificar palavras proibidas"""
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT word FROM banned_words WHERE guild_id = ?', (message.guild.id,))
    banned_words = [row[0].lower() for row in cursor.fetchall()]
    conn.close()
    
    message_lower = message.content.lower()
    
    for word in banned_words:
        if word in message_lower:
            try:
                await message.delete()
                await log_action(message.guild, f"🚫 Mensagem de {message.author.mention} deletada (palavra proibida)")
                await message.author.send(f"❌ Sua mensagem foi deletada por conter uma palavra proibida no servidor {message.guild.name}")
            except:
                pass
            return

async def check_raid_protection(guild, member):
    """Proteção contra raids"""
    current_time = datetime.now()
    raid_data = raid_protection[guild.id]
    
    if raid_data['timeout'] is None or (current_time - raid_data['timeout']).total_seconds() > 60:
        raid_data['count'] = 1
        raid_data['timeout'] = current_time
    else:
        raid_data['count'] += 1
        
        if raid_data['count'] > 10:  # Mais de 10 membros em 1 minuto
            try:
                await member.kick(reason="Raid protection ativada")
                await log_action(guild, f"🛡️ Raid detectado! Membro {member.mention} foi removido.")
            except:
                pass

@tasks.loop(minutes=5)
async def check_spam():
    """Limpar dados de spam a cada 5 minutos"""
    spam_tracking.clear()

# ============================================
# COMANDOS DE MODERAÇÃO
# ============================================

@bot.command(name='kick', aliases=['k'])
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="Nenhuma razão fornecida"):
    """Remover um membro do servidor"""
    if member.top_role >= ctx.author.top_role:
        embed = discord.Embed(
            title="❌ Erro",
            description="Você não pode remover alguém com um cargo igual ou superior ao seu.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    
    try:
        await member.kick(reason=reason)
        embed = discord.Embed(
            title="✅ Membro Removido",
            description=f"{member.mention} foi removido do servidor.",
            color=discord.Color.green()
        )
        embed.add_field(name="Razão", value=reason, inline=False)
        embed.add_field(name="Moderador", value=ctx.author.mention, inline=True)
        await ctx.send(embed=embed)
        await log_action(ctx.guild, f"👢 {member.mention} foi removido por {ctx.author.mention}. Razão: {reason}")
    except Exception as e:
        embed = discord.Embed(title="❌ Erro", description=str(e), color=discord.Color.red())
        await ctx.send(embed=embed)

@bot.command(name='ban', aliases=['b'])
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="Nenhuma razão fornecida"):
    """Banir um membro do servidor"""
    if member.top_role >= ctx.author.top_role:
        embed = discord.Embed(
            title="❌ Erro",
            description="Você não pode banir alguém com um cargo igual ou superior ao seu.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    
    try:
        await member.ban(reason=reason)
        embed = discord.Embed(
            title="✅ Membro Banido",
            description=f"{member.mention} foi banido do servidor.",
            color=discord.Color.green()
        )
        embed.add_field(name="Razão", value=reason, inline=False)
        embed.add_field(name="Moderador", value=ctx.author.mention, inline=True)
        await ctx.send(embed=embed)
        await log_action(ctx.guild, f"🚫 {member.mention} foi banido por {ctx.author.mention}. Razão: {reason}")
    except Exception as e:
        embed = discord.Embed(title="❌ Erro", description=str(e), color=discord.Color.red())
        await ctx.send(embed=embed)

@bot.command(name='mute', aliases=['m'])
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member, duration: int, *, reason="Nenhuma razão fornecida"):
    """Mutar um membro por um tempo (em minutos)"""
    try:
        await member.timeout(timedelta(minutes=duration), reason=reason)
        embed = discord.Embed(
            title="✅ Membro Mutado",
            description=f"{member.mention} foi mutado por {duration} minutos.",
            color=discord.Color.green()
        )
        embed.add_field(name="Razão", value=reason, inline=False)
        embed.add_field(name="Moderador", value=ctx.author.mention, inline=True)
        await ctx.send(embed=embed)
        await log_action(ctx.guild, f"🔇 {member.mention} foi mutado por {duration}m por {ctx.author.mention}. Razão: {reason}")
    except Exception as e:
        embed = discord.Embed(title="❌ Erro", description=str(e), color=discord.Color.red())
        await ctx.send(embed=embed)

@bot.command(name='unmute', aliases=['um'])
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member):
    """Remover mute de um membro"""
    try:
        await member.timeout(None)
        embed = discord.Embed(
            title="✅ Mute Removido",
            description=f"{member.mention} foi desmutado.",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
        await log_action(ctx.guild, f"🔊 Mute removido de {member.mention} por {ctx.author.mention}")
    except Exception as e:
        embed = discord.Embed(title="❌ Erro", description=str(e), color=discord.Color.red())
        await ctx.send(embed=embed)

@bot.command(name='warn', aliases=['w'])
@commands.has_permissions(manage_messages=True)
async def warn(ctx, member: discord.Member, *, reason="Nenhuma razão fornecida"):
    """Avisar um membro"""
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO warns (user_id, guild_id, moderator_id, reason) VALUES (?, ?, ?, ?)',
                   (member.id, ctx.guild.id, ctx.author.id, reason))
    cursor.execute('SELECT COUNT(*) FROM warns WHERE user_id = ? AND guild_id = ?', (member.id, ctx.guild.id))
    warn_count = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    
    embed = discord.Embed(
        title="⚠️ Membro Avisado",
        description=f"{member.mention} recebeu um aviso.",
        color=discord.Color.orange()
    )
    embed.add_field(name="Razão", value=reason, inline=False)
    embed.add_field(name="Total de Avisos", value=warn_count, inline=True)
    embed.add_field(name="Moderador", value=ctx.author.mention, inline=True)
    await ctx.send(embed=embed)
    await log_action(ctx.guild, f"⚠️ {member.mention} avisado por {ctx.author.mention}. Total: {warn_count}. Razão: {reason}")
    
    if warn_count >= 3:
        try:
            await member.kick(reason="3 avisos acumulados")
            await log_action(ctx.guild, f"👢 {member.mention} foi removido por acumular 3 avisos")
        except:
            pass

@bot.command(name='warns')
@commands.has_permissions(manage_messages=True)
async def warns(ctx, member: discord.Member):
    """Ver avisos de um membro"""
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT reason, timestamp, moderator_id FROM warns WHERE user_id = ? AND guild_id = ?',
                   (member.id, ctx.guild.id))
    warns_data = cursor.fetchall()
    conn.close()
    
    if not warns_data:
        embed = discord.Embed(
            title="✅ Sem Avisos",
            description=f"{member.mention} não possui avisos.",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
        return
    
    embed = discord.Embed(
        title=f"⚠️ Avisos de {member.name}",
        description=f"Total: {len(warns_data)} aviso(s)",
        color=discord.Color.orange()
    )
    for i, (reason, timestamp, moderator_id) in enumerate(warns_data, 1):
        embed.add_field(name=f"Aviso #{i}", value=f"**Razão:** {reason}\n**Data:** {timestamp}", inline=False)
    await ctx.send(embed=embed)

@bot.command(name='clearwarn')
@commands.has_permissions(manage_messages=True)
async def clearwarn(ctx, member: discord.Member):
    """Limpar avisos de um membro"""
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM warns WHERE user_id = ? AND guild_id = ?', (member.id, ctx.guild.id))
    conn.commit()
    conn.close()
    
    embed = discord.Embed(
        title="✅ Avisos Limpos",
        description=f"Avisos de {member.mention} foram removidos.",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)
    await log_action(ctx.guild, f"🧹 Avisos de {member.mention} foram limpos por {ctx.author.mention}")

# ============================================
# COMANDOS DE INFORMAÇÃO
# ============================================

@bot.command(name='info')
async def info(ctx, member: discord.Member = None):
    """Informações sobre um membro"""
    if member is None:
        member = ctx.author
    
    embed = discord.Embed(
        title=f"Informações de {member.name}",
        color=member.color,
        timestamp=datetime.now()
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="ID", value=member.id, inline=True)
    embed.add_field(name="Status", value=str(member.status).title(), inline=True)
    embed.add_field(name="Bot", value="Sim ✅" if member.bot else "Não ❌", inline=True)
    embed.add_field(name="Data de Entrada", value=member.joined_at.strftime("%d/%m/%Y %H:%M:%S"), inline=False)
    embed.add_field(name="Conta Criada em", value=member.created_at.strftime("%d/%m/%Y %H:%M:%S"), inline=False)
    embed.add_field(name="Cargos", value=", ".join([role.mention for role in member.roles[1:]]) or "Sem cargos", inline=False)
    
    await ctx.send(embed=embed)

@bot.command(name='serverinfo', aliases=['si'])
async def serverinfo(ctx):
    """Informações sobre o servidor"""
    guild = ctx.guild
    
    embed = discord.Embed(
        title=f"Informações de {guild.name}",
        color=discord.Color.blue(),
        timestamp=datetime.now()
    )
    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
    embed.add_field(name="ID", value=guild.id, inline=True)
    embed.add_field(name="Dono", value=guild.owner.mention, inline=True)
    embed.add_field(name="Membros", value=guild.member_count, inline=True)
    embed.add_field(name="Canais", value=len(guild.channels), inline=True)
    embed.add_field(name="Cargos", value=len(guild.roles), inline=True)
    embed.add_field(name="Criado em", value=guild.created_at.strftime("%d/%m/%Y %H:%M:%S"), inline=False)
    embed.add_field(name="Nível de Verificação", value=str(guild.verification_level).title(), inline=True)
    
    await ctx.send(embed=embed)

@bot.command(name='avatar')
async def avatar(ctx, member: discord.Member = None):
    """Ver avatar de um membro"""
    if member is None:
        member = ctx.author
    
    embed = discord.Embed(
        title=f"Avatar de {member.name}",
        color=discord.Color.blue()
    )
    embed.set_image(url=member.display_avatar.url)
    embed.add_field(name="Link", value=f"[Clique aqui]({member.display_avatar.url})", inline=False)
    await ctx.send(embed=embed)

# ============================================
# COMANDOS DE CONFIGURAÇÃO
# ============================================

@bot.command(name='setlog')
@commands.has_permissions(administrator=True)
async def setlog(ctx, channel: discord.TextChannel):
    """Configurar canal de logs"""
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO config (guild_id, log_channel_id) VALUES (?, ?)',
                   (ctx.guild.id, channel.id))
    conn.commit()
    conn.close()
    
    embed = discord.Embed(
        title="✅ Canal de Logs Configurado",
        description=f"Logs serão enviados para {channel.mention}",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

@bot.command(name='setautorole')
@commands.has_permissions(administrator=True)
async def setautorole(ctx, role: discord.Role):
    """Configurar autorole para novos membros"""
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO config (guild_id, autorole_id) VALUES (?, ?)',
                   (ctx.guild.id, role.id))
    conn.commit()
    conn.close()
    
    embed = discord.Embed(
        title="✅ Autorole Configurado",
        description=f"Novos membros receberão {role.mention}",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

@bot.command(name='addbannedword')
@commands.has_permissions(manage_messages=True)
async def addbannedword(ctx, *, word):
    """Adicionar palavra proibida"""
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO banned_words (guild_id, word) VALUES (?, ?)',
                   (ctx.guild.id, word.lower()))
    conn.commit()
    conn.close()
    
    embed = discord.Embed(
        title="✅ Palavra Proibida Adicionada",
        description=f"'{word}' foi adicionada à lista de palavras proibidas.",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

@bot.command(name='removebannedword')
@commands.has_permissions(manage_messages=True)
async def removebannedword(ctx, *, word):
    """Remover palavra proibida"""
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM banned_words WHERE guild_id = ? AND word = ?',
                   (ctx.guild.id, word.lower()))
    conn.commit()
    conn.close()
    
    embed = discord.Embed(
        title="✅ Palavra Removida",
        description=f"'{word}' foi removida da lista de palavras proibidas.",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

@bot.command(name='listbannedwords')
@commands.has_permissions(manage_messages=True)
async def listbannedwords(ctx):
    """Listar palavras proibidas"""
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT word FROM banned_words WHERE guild_id = ?', (ctx.guild.id,))
    words = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    if not words:
        embed = discord.Embed(
            title="📋 Palavras Proibidas",
            description="Nenhuma palavra proibida configurada.",
            color=discord.Color.blue()
        )
    else:
        embed = discord.Embed(
            title="📋 Palavras Proibidas",
            description=", ".join(words),
            color=discord.Color.blue()
        )
    await ctx.send(embed=embed)

# ============================================
# SISTEMA DE REPUTAÇÃO
# ============================================

@bot.command(name='rep', aliases=['+rep'])
async def add_reputation(ctx, member: discord.Member):
    """Dar reputação a um membro"""
    if member == ctx.author:
        embed = discord.Embed(
            title="❌ Erro",
            description="Você não pode dar reputação para si mesmo.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT points FROM reputation WHERE user_id = ? AND guild_id = ?',
                   (member.id, ctx.guild.id))
    result = cursor.fetchone()
    
    if result:
        new_points = result[0] + 1
        cursor.execute('UPDATE reputation SET points = ? WHERE user_id = ? AND guild_id = ?',
                       (new_points, member.id, ctx.guild.id))
    else:
        cursor.execute('INSERT INTO reputation (user_id, guild_id, points) VALUES (?, ?, ?)',
                       (member.id, ctx.guild.id, 1))
        new_points = 1
    
    conn.commit()
    conn.close()
    
    embed = discord.Embed(
        title=f"⭐ Reputação de {member.name}",
        description=f"{member.mention} agora tem {new_points} ponto(s) de reputação!",
        color=discord.Color.gold()
    )
    await ctx.send(embed=embed)

@bot.command(name='reputation', aliases=['rep-check', 'myrep'])
async def check_reputation(ctx, member: discord.Member = None):
    """Verificar reputação de um membro"""
    if member is None:
        member = ctx.author
    
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT points FROM reputation WHERE user_id = ? AND guild_id = ?',
                   (member.id, ctx.guild.id))
    result = cursor.fetchone()
    conn.close()
    
    points = result[0] if result else 0
    
    embed = discord.Embed(
        title=f"⭐ Reputação de {member.name}",
        description=f"{member.mention} tem **{points}** ponto(s) de reputação",
        color=discord.Color.gold()
    )
    await ctx.send(embed=embed)

@bot.command(name='top-reputation', aliases=['top-rep'])
async def top_reputation(ctx):
    """Top 10 membros com mais reputação"""
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT user_id, points FROM reputation WHERE guild_id = ? ORDER BY points DESC LIMIT 10',
                   (ctx.guild.id,))
    results = cursor.fetchall()
    conn.close()
    
    if not results:
        embed = discord.Embed(
            title="🏆 Top Reputação",
            description="Ninguém tem reputação ainda.",
            color=discord.Color.gold()
        )
        await ctx.send(embed=embed)
        return
    
    embed = discord.Embed(
        title="🏆 Top 10 - Reputação",
        color=discord.Color.gold()
    )
    
    medals = ['🥇', '🥈', '🥉']
    for i, (user_id, points) in enumerate(results, 1):
        user = ctx.guild.get_member(user_id)
        medal = medals[i-1] if i <= 3 else f"{i}."
        embed.add_field(
            name=f"{medal} {user.name if user else f'Usuário {user_id}'}",
            value=f"⭐ {points} pontos",
            inline=False
        )
    
    await ctx.send(embed=embed)

# ============================================
# COMANDOS DE TICKETS
# ============================================

@bot.command(name='ticket')
async def create_ticket(ctx):
    """Criar um ticket"""
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO tickets (guild_id, user_id) VALUES (?, ?)',
                   (ctx.guild.id, ctx.author.id))
    ticket_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    # Criar canal privado
    try:
        channel = await ctx.guild.create_text_channel(
            name=f"ticket-{ticket_id}",
            category=None,
            overwrites={
                ctx.guild.default_role: discord.PermissionOverwrite(view_channel=False),
                ctx.author: discord.PermissionOverwrite(view_channel=True, send_messages=True),
                ctx.guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
            }
        )
        
        embed = discord.Embed(
            title="🎫 Ticket Criado",
            description=f"Seu ticket foi criado: {channel.mention}",
            color=discord.Color.green()
        )
        embed.add_field(name="ID do Ticket", value=ticket_id, inline=True)
        embed.add_field(name="Status", value="Aberto", inline=True)
        await ctx.send(embed=embed)
        
        # Mensagem no canal do ticket
        embed2 = discord.Embed(
            title="🎫 Novo Ticket",
            description=f"Bem-vindo {ctx.author.mention}!\n\nDescreva seu problema abaixo. A equipe responderá em breve.",
            color=discord.Color.blue()
        )
        embed2.add_field(name="Para fechar o ticket", value="Use `!closeticket`", inline=False)
        await channel.send(embed=embed2)
        
        # Atualizar no banco
        conn = sqlite3.connect('bot_data.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE tickets SET channel_id = ? WHERE ticket_id = ?', (channel.id, ticket_id))
        conn.commit()
        conn.close()
    except Exception as e:
        embed = discord.Embed(title="❌ Erro", description=str(e), color=discord.Color.red())
        await ctx.send(embed=embed)

@bot.command(name='closeticket')
async def close_ticket(ctx):
    """Fechar um ticket"""
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT ticket_id FROM tickets WHERE channel_id = ? AND closed = 0', (ctx.channel.id,))
    result = cursor.fetchone()
    
    if not result:
        embed = discord.Embed(
            title="❌ Erro",
            description="Este não é um canal de ticket.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        conn.close()
        return
    
    ticket_id = result[0]
    cursor.execute('UPDATE tickets SET closed = 1 WHERE ticket_id = ?', (ticket_id,))
    conn.commit()
    conn.close()
    
    embed = discord.Embed(
        title="✅ Ticket Fechado",
        description=f"Ticket #{ticket_id} foi fechado.",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)
    
    # Deletar canal após 5 segundos
    await asyncio.sleep(5)
    try:
        await ctx.channel.delete()
    except:
        pass

# ============================================
# COMANDO DE AJUDA
# ============================================

@bot.command(name='help', aliases=['h', '?'])
async def help_command(ctx, command_name=None):
    """Ajuda sobre os comandos"""
    if command_name is None:
        embed = discord.Embed(
            title=f"📚 Ajuda - {bot.user.name}",
            description="Use `!help [comando]` para mais informações",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="🛡️ Moderação",
            value="`!kick` `!ban` `!mute` `!unmute` `!warn` `!warns` `!clearwarn`",
            inline=False
        )
        embed.add_field(
            name="📋 Informações",
            value="`!info` `!serverinfo` `!avatar`",
            inline=False
        )
        embed.add_field(
            name="⭐ Reputação",
            value="`!rep` `!reputation` `!top-reputation`",
            inline=False
        )
        embed.add_field(
            name="🎫 Tickets",
            value="`!ticket` `!closeticket`",
            inline=False
        )
        embed.add_field(
            name="⚙️ Configuração",
            value="`!setlog` `!setautorole` `!addbannedword` `!removebannedword` `!listbannedwords`",
            inline=False
        )
        
        await ctx.send(embed=embed)
    else:
        # Mostrar ajuda específica do comando
        cmd = bot.get_command(command_name)
        if cmd is None:
            embed = discord.Embed(
                title="❌ Comando não encontrado",
                description=f"O comando `{command_name}` não existe.",
                color=discord.Color.red()
            )
        else:
            embed = discord.Embed(
                title=f"📚 Ajuda - {cmd.name}",
                description=cmd.help or "Sem descrição",
                color=discord.Color.blue()
            )
            embed.add_field(name="Aliases", value=", ".join(cmd.aliases) if cmd.aliases else "Nenhum", inline=False)
        
        await ctx.send(embed=embed)

# ============================================
# INICIAR BOT
# ============================================

if __name__ == "__main__":
    if not TOKEN:
        print("❌ ERRO: Token não encontrado! Configure o arquivo .env")
        exit(1)
    
    print("🚀 Iniciando bot...")
    bot.run(TOKEN)
