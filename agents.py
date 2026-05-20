from crewai import Agent, LLM
from tools import SearchFlightsTool, SearchLocalActivitiesTool
import os

# Initialize the LM Studio LLM
# Base URL is read from environment variable to support Docker deployments.
llm_base_url = os.getenv("LLM_BASE_URL", "http://host.docker.internal:1234/v1")

llm = LLM(
    model="openai/gemma-4-31b", # Adjust if necessary based on what is loaded in LM Studio
    base_url=llm_base_url,
    api_key="lm-studio",
    temperature=0.7
)

flight_searcher = Agent(
    role="Senior Flight Search Specialist",
    goal="Find the best flight routes to Germany based on strict user parameters, including specific layover requirements.",
    backstory=(
        "You are an expert travel agent specializing in complex flight routing. "
        "You know how to manipulate search parameters to find hidden gems, "
        "including intentionally long layovers that allow for mini-vacations "
        "in transit cities."
    ),
    verbose=True,
    allow_delegation=False,
    tools=[SearchFlightsTool()],
    llm=llm
)

spot_analyzer = Agent(
    role="Local Experience & Transit Activity Specialist",
    goal="Analyze layover cities to find specific activities, spots, or experiences tailored exactly to the user's free-text request.",
    backstory=(
        "You are an expert local guide and travel planner. You specialize in "
        "crafting custom micro-itineraries for short layovers. You carefully read "
        "the user's desired activities (e.g., saunas, breweries, brutalist architecture) "
        "and find the best matches accessible from the transit airport."
    ),
    verbose=True,
    allow_delegation=False,
    tools=[SearchLocalActivitiesTool()],
    llm=llm
)

itinerary_optimizer = Agent(
    role="Itinerary Optimization Manager",
    goal="Synthesize flight data and sightseeing analysis to create 3 optimized travel plans.",
    backstory=(
        "You are a master travel coordinator. You take raw flight data and "
        "destination analysis to craft perfect itineraries. You understand that "
        "different travelers have different priorities, so you always provide "
        "options ranging from pure efficiency to specialized sightseeing experiences."
    ),
    verbose=True,
    allow_delegation=False,
    llm=llm
)
