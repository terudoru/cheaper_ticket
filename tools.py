import json
from crewai.tools import BaseTool
from models import FlightSearchParams

class SearchFlightsTool(BaseTool):
    name: str = "Search Flights Mock API"
    description: str = "Search for flights based on strict parameters including layover times. Provide input as a JSON string matching FlightSearchParams."

    def _run(self, input_data: str) -> str:
        try:
            data = json.loads(input_data)
            params = FlightSearchParams(**data)
        except Exception as e:
            return f"Error parsing input: {e}. Please provide a valid JSON string matching the FlightSearchParams schema."

        # Mocking the response from a flight API
        mock_response = [
            {
                "id": "FL-001",
                "airline": "FastAir",
                "price": 1200.0,
                "duration_hours": 14.5,
                "layover_city": "Helsinki",
                "layover_duration_hours": 2.5,
                "route": f"{params.origin} -> HEL -> {params.destination}"
            },
            {
                "id": "FL-002",
                "airline": "ExploreAir",
                "price": 950.0,
                "duration_hours": 28.0,
                "layover_city": "Warsaw",
                "layover_duration_hours": 15.0,
                "route": f"{params.origin} -> WAW -> {params.destination}"
            },
            {
                "id": "FL-003",
                "airline": "EuroWings",
                "price": 1050.0,
                "duration_hours": 22.0,
                "layover_city": "Prague",
                "layover_duration_hours": 10.0,
                "route": f"{params.origin} -> PRG -> {params.destination}"
            }
        ]
        
        # Filter based on layover parameters
        filtered_flights = []
        for flight in mock_response:
            layover = flight["layover_duration_hours"]
            if params.min_layover_hours is not None and layover < params.min_layover_hours:
                continue
            if params.max_layover_hours is not None and layover > params.max_layover_hours:
                continue
            filtered_flights.append(flight)

        return json.dumps(filtered_flights, indent=2)

class SearchLocalActivitiesTool(BaseTool):
    name: str = "Search Local Activities Mock API"
    description: str = "Search for local activities, spots, or experiences in a specific city based on a user's intent. Input should be a JSON string containing 'city' and 'intent'."

    def _run(self, query: str) -> str:
        try:
            data = json.loads(query)
            city = data.get("city", "").lower().strip()
            intent = data.get("intent", "").lower()
        except:
            # Fallback if the agent just passes a string
            city = query.lower().strip()
            intent = query.lower().strip()

        spots = []
        
        # Dynamic mock generation based on keywords
        if "サウナ" in intent or "sauna" in intent:
            spots.append({
                "name": "Löyly Helsinki",
                "type": "Sauna / Wellness",
                "description": "A stunning public sauna complex on the Helsinki waterfront.",
                "distance_from_airport": "30 mins by train"
            })
        elif "ビール" in intent or "beer" in intent or "醸造所" in intent:
            spots.append({
                "name": "U Fleků",
                "type": "Brewery",
                "description": "A historic pub and microbrewery in Prague dating back to 1499.",
                "distance_from_airport": "40 mins by public transport"
            })
        elif "テクノ" in intent or "club" in intent or "music" in intent:
            spots.append({
                "name": "Smolna",
                "type": "Techno Club",
                "description": "One of Warsaw's premier underground electronic music venues.",
                "distance_from_airport": "20 mins by taxi"
            })
        else:
            # Fallback to the original Brutalism requirement if no specific keywords match
            spots.extend([
                {
                    "name": f"Central Monument of {city.capitalize()}",
                    "type": "Architecture",
                    "description": f"A notable architectural landmark in {city.capitalize()}.",
                    "distance_from_airport": "25 mins by train"
                }
            ])

        return json.dumps({
            "city": city,
            "spots": spots,
            "suitability_score": len(spots) * 4 if len(spots) > 0 else 2
        }, indent=2)
