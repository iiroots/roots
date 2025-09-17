import os
import discord
from random import shuffle
import asyncio

# Define as permissões (intents) que o bot precisa
intents = discord.Intents.default()
intents.message_content = True

# Inicializa o bot com as permissões
client = discord.Client(intents=intents)

# Evento para quando o bot entra online
@client.event
async def on_ready():
    print(f'Bot logado como: {client.user}')
    print('Pronto para sortear times!')

# Função para realizar o sorteio e enviar a resposta
async def perform_raffle(message, all_players):
    # Embaralha a lista completa de jogadores
    shuffle(all_players)
    
    # Define os times
    time1 = all_players[:5]
    time2 = all_players[5:10]

    # Formata a mensagem de resposta
    response = "**TIMES SORTEADOS!**\n\n"
    response += "**TIME QUE VAI PERDER:**\n" + "\n".join(f"- {p}" for p in time1) + "\n\n"
    response += "**TIME QUE SÓ PERDE:**\n" + "\n".join(f"- {p}" for p in time2) + "\n"

    await message.channel.send(response)

# Evento que lida com as mensagens
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!sortear'):
        await message.channel.send("Manda o nick dos 10 noobs aí (separados por vírgula): ")

        def check(m):
            return m.author == message.author and m.channel == message.channel

        try:
            msg = await client.wait_for('message', check=check, timeout=60.0)
            input_nicks = [nick.strip() for nick in msg.content.split(',') if nick.strip()]
            
            # Garante que há no mínimo 10 jogadores, preenchendo com "COMPLETE" se necessário
            players = input_nicks
            if len(players) < 10:
                for i in range(10 - len(players)):
                    players.append(f"COMPLETE {i+1}")

            await perform_raffle(message, players)

            # Lida com a opção de re-sortear
            while True:
                await message.channel.send("\nTem gente chorando? Digite **sim** para sortear de novo.")

                def check_sim(m):
                    return m.author == message.author and m.channel == message.channel

                try:
                    response_msg = await client.wait_for('message', check=check_sim, timeout=30.0)
                    if response_msg.content.lower() in ['sim', 's']:
                        await message.channel.send("Ok, sorteando de novo...")
                        await perform_raffle(message, players)
                    else:
                        await message.channel.send("GL HF\nQue o menos pior vença!")
                        break
                except asyncio.TimeoutError:
                    await message.channel.send("Tempo esgotado para o re-sorteio. GL HF!")
                    break

        except asyncio.TimeoutError:
            await message.channel.send("Tempo esgotado! Sorteio cancelado.")
            return

client.run(os.environ['DISCORD_BOT_TOKEN'])
