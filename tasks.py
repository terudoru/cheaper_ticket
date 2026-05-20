from crewai import Task
from agents import flight_searcher, spot_analyzer, itinerary_optimizer
import textwrap

def create_search_task(params_json: str):
    return Task(
        description=textwrap.dedent(f"""
            Search for flights to Germany using the provided search parameters.
            
            Parameters (JSON):
            {params_json}
            
            You must use your Search Flights Mock API tool to fetch flight data.
            Pay special attention to the layover times. If the user asks for 
            a minimum layover (e.g., 10 hours), ensure you find flights that match this constraint.
            
            Output the raw flight options found, specifically highlighting the layover cities 
            and the duration of those layovers.
        """),
        expected_output="A list of flight options that meet the criteria, with clear details on layover cities and durations.",
        agent=flight_searcher
    )

def create_analyze_task(params_json: str):
    import json
    try:
        data = json.loads(params_json)
        desired_activities = data.get("desired_activities", "Explore general architecture")
    except:
        desired_activities = "Explore general architecture"

    return Task(
        description=textwrap.dedent(f"""
            Review the flight options provided by the Flight Searcher.
            Extract the layover cities from those flights.
            
            The user has specifically requested the following activities/intent for their layover:
            "{desired_activities}"
            
            For each layover city, use your Search Local Activities Mock API tool to find 
            spots, activities, or experiences that match this specific intent. 
            Pass the city and the intent to your tool.
            
            Calculate a score for each city based on the quantity and quality of the matching spots found.
            
            Output a comprehensive report of each layover city and its suitability for the user's custom intent.
        """),
        expected_output="A detailed report on each layover city, listing matching activity spots and a suitability score.",
        agent=spot_analyzer
    )

def create_optimize_task(params_json: str):
    import json
    try:
        data = json.loads(params_json)
        desired_activities = data.get("desired_activities", "Explore general architecture")
    except:
        desired_activities = "Explore general architecture"

    return Task(
        description=textwrap.dedent(f"""
            You have the flight options from the Flight Searcher and the custom activity 
            analysis from the Local Experience Specialist.
            
            The user specifically wants to: "{desired_activities}" during their layover.
            
            Synthesize this information to create 3 distinct travel plans:
            1. Cheapest/Fastest Plan: Prioritizes low cost and short total travel time (efficiency).
            2. Custom Activity Pilgrimage Plan: Selects a flight with a long layover (e.g., 10-24 hours) 
               in a city that scored highly for the user's specific request ("{desired_activities}"). 
               Include the activity spots found.
            3. Comprehensive Balance Plan: A compromise between price, speed, and a moderate amount of custom activities.
            
            Present these plans clearly in a markdown format.
        """),
        expected_output="A markdown document detailing the 3 specific travel plans (Cheapest/Fastest, Custom Activity Pilgrimage, Comprehensive Balance).",
        agent=itinerary_optimizer
    )
