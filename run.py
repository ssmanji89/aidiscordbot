from discord import *
import openai
import requests
import openai
import sqlite3
import os
import logging

DISCORD_BOT_TOKEN = TOKEN = 'YOUR_DISCORD_BOT_TOKEN'
openai.api_key = 'YOUR_OPENAI_API_KEY'

# Initialize logging
logging.basicConfig(level=logging.INFO)

bot = commands.Bot(command_prefix='!')

# In-memory database for tickets and knowledge base
tickets = {}
knowledge_base = {
    "installation_error": "Have you tried turning it off and on again?",
    "login_error": "Please ensure your username and password are correct."
}

def ask_openai(query):
    """Get technical assistance from OpenAI."""
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=f"Technical support request: {query}. Provide immediate resolution options.",
        max_tokens=150
    )
    return response.choices[0].text.strip()

import requests

def fetch_weather(location):
    API_ENDPOINT = "http://api.openweathermap.org/data/2.5/weather"
    API_KEY = "YOUR_OPENWEATHERMAP_API_KEY"
    response = requests.get(API_ENDPOINT, params={
        "q": location,
        "appid": API_KEY
    })
    if response.status_code == 200:
        data = response.json()
        return data["weather"][0]["description"]
    return "Unable to fetch weather data."

def fetch_uv_index(location):
    # Using OpenWeatherMap for UV index as an example
    API_ENDPOINT = "http://api.openweathermap.org/data/2.5/uvi"
    API_KEY = "YOUR_OPENWEATHERMAP_API_KEY"
    lat, lon = location.split(",") # assuming location format as "lat,lon"
    response = requests.get(API_ENDPOINT, params={
        "lat": lat,
        "lon": lon,
        "appid": API_KEY
    })
    if response.status_code == 200:
        data = response.json()
        return f"UV Index for {location}: {data['value']}"
    return "Unable to fetch UV index."

def fetch_sports_news():
    API_ENDPOINT = "https://newsapi.org/v2/top-headlines"
    API_KEY = "YOUR_NEWSAPI_KEY"
    response = requests.get(API_ENDPOINT, params={
        "category": "sports",
        "apiKey": API_KEY,
        "pageSize": 5
    })
    if response.status_code == 200:
        data = response.json()
        headlines = [article["title"] for article in data["articles"]]
        return "\n".join(headlines)
    return "Unable to fetch sports news."

def fetch_movie_info(title):
    API_ENDPOINT = "http://www.omdbapi.com/"
    API_KEY = "YOUR_OMDBAPI_KEY"
    response = requests.get(API_ENDPOINT, params={
        "t": title,
        "apikey": API_KEY
    })
    if response.status_code == 200:
        data = response.json()
        if data["Response"] == "True":
            return data["Plot"]
        else:
            return data["Error"]
    return "Unable to fetch movie information."

def fetch_exchange_rates(base_currency):
    API_ENDPOINT = "https://api.exchangerate-api.com/v4/latest/"
    response = requests.get(API_ENDPOINT + base_currency)
    if response.status_code == 200:
        data = response.json()
        rates = data["rates"]
        return f"Exchange rates for {base_currency}: {rates}"
    return "Unable to fetch exchange rates."

def fetch_covid_stats(region):
    API_ENDPOINT = f"https://disease.sh/v3/covid-19/countries/{region}"
    response = requests.get(API_ENDPOINT)
    if response.status_code == 200:
        data = response.json()
        stats = {
            "Cases": data["cases"],
            "Deaths": data["deaths"],
            "Recovered": data["recovered"],
            "Active": data["active"],
        }
        return stats
    return "Unable to fetch COVID-19 stats."

def fetch_dictionary_definition(word):
    # Using DictionaryAPI as an example
    API_ENDPOINT = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    response = requests.get(API_ENDPOINT)
    if response.status_code == 200:
        data = response.json()
        definition = data[0]['meanings'][0]['definitions'][0]['definition']
        return definition
    return "Unable to fetch the definition."

FUNCTION_REGISTRY = {
    'fetch_weather': fetch_weather,
    'fetch_uv_index': fetch_uv_index,
    'fetch_sports_news': fetch_sports_news,
    'fetch_movie_info': fetch_movie_info,
    'fetch_exchange_rates': fetch_exchange_rates,
    'fetch_covid_stats': fetch_covid_stats,
    'fetch_dictionary_definition': fetch_dictionary_definition,
}


@bot.command(name='ask')
async def ask_support(ctx, *, query):
    ticket_id = len(tickets) + 1
    tickets[ticket_id] = {
        "user": ctx.author.name,
        "description": query,
        "status": "open"
    }
    ai_response = ask_openai(query)
    
    # DM the user with potential solutions and wait for their response
    dm_channel = await ctx.author.create_dm()
    await dm_channel.send(f"Based on your query, here's a potential solution: {ai_response}\n\nDid this resolve your issue? (Yes/No)")
    
    # Check for user response in DM
    def check(message):
        return message.author == ctx.author and message.channel == dm_channel and message.content.lower() in ["yes", "no"]
    
    try:
        user_response = await bot.wait_for('message', timeout=60.0, check=check)
        if user_response.content.lower() == "yes":
            tickets[ticket_id]['status'] = 'resolved'
            await dm_channel.send("Great! Your ticket has been resolved. If you have further issues, please let us know.")
        else:
            await dm_channel.send("Sorry to hear that. We'll escalate your ticket for further review by our support team. Thank you for your patience!")
    except discord.errors.TimeoutError:
        await dm_channel.send("Did not receive a response in time. Your ticket remains open. Please reply with 'Yes' or 'No' when you can.")

# Additional commands for knowledge base, creating tickets, closing tickets, and feedback
@bot.command(name='knowledge_base')
async def check_knowledge_base(ctx, *, query):
    for keyword, solution in knowledge_base.items():
        if keyword in query.lower():
            await ctx.send(f"Based on your query, here's a potential solution: {solution}")
            return
    await ctx.send("I couldn't find an immediate solution in the knowledge base.")

@bot.command(name='create_ticket')
async def create_ticket(ctx, *, description):
    ticket_id = len(tickets) + 1
    tickets[ticket_id] = {
        "user": ctx.author.name,
        "description": description,
        "status": "open"
    }
    await ctx.send(f"Your ticket has been created with ID #{ticket_id}.")

@bot.command(name='close_ticket')
async def close_ticket(ctx, ticket_id: int):
    if ticket_id in tickets and tickets[ticket_id]['user'] == ctx.author.name:
        tickets[ticket_id]['status'] = 'closed'
        await ctx.send(f"Ticket #{ticket_id} has been closed. Thank you!")
    else:
        await ctx.send("You don't have permission to close this ticket or the ticket doesn't exist.")

@bot.command(name='feedback')
async def feedback(ctx, *, feedback_text):
    # Store the feedback for later analysis. For this mock implementation, we'll just print it.
    print(f"Feedback from {ctx.author.name}: {feedback_text}")
    await ctx.send("Thank you for your feedback!")

# For admin or support staff to view all open tickets.
@bot.command(name='view_tickets')
@commands.has_role('SupportStaff')  # Only members with the "SupportStaff" role can execute this command.
async def view_tickets(ctx):
    open_tickets = [f"Ticket ID: {ticket_id} - {data['description']}" for ticket_id, data in tickets.items() if data['status'] == 'open']
    if open_tickets:
        await ctx.send("\n".join(open_tickets))
    else:
        await ctx.send("No open tickets.")



# Initialize SQLite database for tickets and knowledge base
conn = sqlite3.connect('tickets.db')
c = conn.cursor()

def setup_database():
    c.execute("CREATE TABLE IF NOT EXISTS tickets (id INTEGER PRIMARY KEY AUTOINCREMENT, query TEXT, response TEXT, feedback TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS knowledge_base (id INTEGER PRIMARY KEY AUTOINCREMENT, issue TEXT, solution TEXT)")
    conn.commit()

def ask_openai(query):
    try:
        # Your OpenAI API logic here
        response = "OpenAI response"
        confidence_level = 0.9  # Simulated confidence level
    except Exception as e:
        logging.error(f"Error in OpenAI API call: {e}")
        return "An error occurred while connecting to OpenAI", 0.0
    return response, confidence_level

@bot.command()
async def ticket(ctx, *, query):
    response, confidence = ask_openai(query)
    c.execute("INSERT INTO tickets (query, response) VALUES (?, ?)", (query, response))
    conn.commit()
    ticket_id = c.lastrowid
    await ctx.send(f"Ticket created: {response} \n Your ticket ID is: {ticket_id}. \n Was this response helpful? (Yes/No)")

@bot.command()
async def feedback(ctx, ticket_id: int, feedback: str):
    c.execute("UPDATE tickets SET feedback = ? WHERE id = ?", (feedback.lower(), ticket_id))
    conn.commit()
    await ctx.send(f"Feedback for ticket ID {ticket_id} has been recorded as {feedback}.")

@tasks.loop(hours=24)
async def update_knowledge_base():
    c.execute("SELECT query, response FROM tickets WHERE feedback = 'yes'")
    for row in c.fetchall():
        query, response = row
        c.execute("INSERT INTO knowledge_base (issue, solution) VALUES (?, ?)", (query, response))
    conn.commit()

@bot.command()
@commands.has_role('Admin')
async def manual_kb_update(ctx, issue: str, solution: str):
    c.execute("INSERT INTO knowledge_base (issue, solution) VALUES (?, ?)", (issue, solution))
    conn.commit()
    await ctx.send(f"Knowledge base updated with issue: {issue} and solution: {solution}.")

@bot.event
async def on_ready():
    logging.info(f"Logged in as {bot.user}!")
    update_knowledge_base.start()

if __name__ == "__main__":
    setup_database()
    bot.run(DISCORD_BOT_TOKEN)


# Run the bot
bot.run(TOKEN)
