@bot.tree.command(name="resume-chat", description="Résume les 50 derniers messages du salon")
async def resume_chat(interaction: discord.Interaction):
    await interaction.response.defer()

    try:
        messages = []
        async for message in interaction.channel.history(limit=50):
            if not message.author.bot and message.content:
                messages.append(f"{message.author.name}: {message.content}")

        messages.reverse()

        if not messages:
            await interaction.followup.send("❌ Aucun message à résumer !")
            return

        conversation = "\n".join(messages)

        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {os.getenv('GROQ_KEY')}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama3-8b-8192",
                    "max_tokens": 500,
                    "messages": [
                        {
                            "role": "system",
                            "content": "Tu es un assistant qui résume des conversations Discord en français de façon claire et concise."
                        },
                        {
                            "role": "user",
                            "content": f"Résume cette conversation Discord en 5 lignes maximum :\n\n{conversation}"
                        }
                    ]
                }
            ) as resp:
                data = await resp.json()
                resume = data["choices"][0]["message"]["content"]

        embed = discord.Embed(title="📝 Résumé du chat", description=resume, color=0x00bfff)
        await interaction.followup.send(embed=embed)

    except Exception as e:
        await interaction.followup.send(f"❌ Erreur : `{e}`")
