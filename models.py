from pydantic import BaseModel, Field
from typing import List, Optional

class FlightSearchParams(BaseModel):
    """Parameters for searching flights."""
    origin: str = Field(..., description="Departure airport code (e.g., KIJ, HND, NRT)")
    destination: str = Field(..., description="Destination airport code (e.g., BER, FRA)")
    departure_date_start: str = Field(..., description="Start of departure date range (YYYY-MM-DD)")
    departure_date_end: str = Field(..., description="End of departure date range (YYYY-MM-DD)")
    max_transfers: int = Field(default=3, description="Maximum number of transfers (0-3)")
    max_flight_hours: Optional[int] = Field(default=None, description="Maximum total flight time in hours")
    departure_time_start: Optional[str] = Field(default=None, description="Preferred earliest departure time (HH:MM)")
    departure_time_end: Optional[str] = Field(default=None, description="Preferred latest departure time (HH:MM)")
    arrival_time_start: Optional[str] = Field(default=None, description="Preferred earliest arrival time (HH:MM)")
    arrival_time_end: Optional[str] = Field(default=None, description="Preferred latest arrival time (HH:MM)")
    min_layover_hours: Optional[int] = Field(default=0, description="Minimum layover time in hours")
    max_layover_hours: Optional[int] = Field(default=24, description="Maximum layover time in hours")
    include_carry_on: bool = Field(default=True, description="Include carry-on baggage in price calculation")
    include_checked_bag: bool = Field(default=True, description="Include checked baggage in price calculation")
    excluded_airlines: List[str] = Field(default_factory=list, description="List of airline codes to exclude")
    desired_activities: Optional[str] = Field(default=None, description="Free-text description of what the user wants to do during the layover")

class ActivitySpot(BaseModel):
    """Represents a specific sightseeing or activity spot."""
    name: str = Field(..., description="Name of the spot")
    type: str = Field(..., description="Type of activity or place")
    description: str = Field(..., description="Brief description of the spot")
    distance_from_airport: str = Field(..., description="Approximate distance from the airport")

class LayoverCityAnalysis(BaseModel):
    """Analysis of a layover city for custom sightseeing."""
    city: str = Field(..., description="Name of the layover city")
    layover_duration_hours: int = Field(..., description="Layover duration in hours")
    spots: List[ActivitySpot] = Field(default_factory=list, description="List of found activity spots matching user intent")
    suitability_score: int = Field(..., description="Score out of 10 for suitability during layover based on user intent")

class FlightItinerary(BaseModel):
    """Represents a specific flight itinerary."""
    id: str = Field(..., description="Unique identifier for the itinerary")
    price: float = Field(..., description="Total price including baggage")
    duration_hours: float = Field(..., description="Total duration including layovers")
    layover_city: Optional[str] = Field(default=None, description="City where a long layover occurs")
    layover_duration_hours: Optional[float] = Field(default=None, description="Duration of the layover in hours")

class OptimizedPlans(BaseModel):
    """The final 3 optimized plans."""
    cheapest_fastest_plan: FlightItinerary = Field(..., description="Plan prioritizing speed and low cost")
    custom_activity_plan: FlightItinerary = Field(..., description="Plan with a layover tailored to the user's desired activities")
    comprehensive_balance_plan: FlightItinerary = Field(..., description="Plan balancing cost, speed, and sightseeing")
