import json
from crewai import Crew, Process
from models import FlightSearchParams
from agents import flight_searcher, spot_analyzer, itinerary_optimizer
from tasks import create_search_task, create_analyze_task, create_optimize_task

def main():
    print("Initializing Flight Search Multi-Agent System...")

    # Define the initial parameters for the search
    # User request: Niigata (KIJ) to Berlin (BER) in August, looking for a 10-24 hour layover
    search_params = FlightSearchParams(
        origin="KIJ",
        destination="BER",
        departure_date_start="2026-08-01",
        departure_date_end="2026-08-10",
        max_transfers=2,
        min_layover_hours=10,
        max_layover_hours=24,
        include_carry_on=True,
        include_checked_bag=True,
        excluded_airlines=[]
    )
    
    params_json = search_params.model_dump_json(indent=2)
    print(f"Search Parameters:\n{params_json}\n")

    # Create tasks
    search_task = create_search_task(params_json)
    analyze_task = create_analyze_task()
    optimize_task = create_optimize_task()

    # Assemble the crew
    flight_crew = Crew(
        agents=[flight_searcher, spot_analyzer, itinerary_optimizer],
        tasks=[search_task, analyze_task, optimize_task],
        process=Process.sequential,
        verbose=True # set to True or 2 to see the execution logs
    )

    print("Kicking off the crew...")
    result = flight_crew.kickoff()

    print("\n================================================")
    print("FINAL OPTIMIZED ITINERARIES")
    print("================================================\n")
    print(result)

if __name__ == "__main__":
    main()
