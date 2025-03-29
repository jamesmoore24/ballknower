from pydantic import BaseModel, Field, HttpUrl
from typing import Optional
import datetime

# ---------------------------
# Books Payload
# ---------------------------
class BookPayload(BaseModel):
    id: Optional[int] = None  # Auto-generated on insertion.
    name: str                   # e.g., "PrizePicks", "FanDuel"
    tier: int                   # 1, 2, or 3 based on market sharpness.
    website: Optional[HttpUrl] = None  # Optional URL for reference or automated login.

# ---------------------------
# Teams Payload
# ---------------------------
class TeamPayload(BaseModel):
    id: Optional[int] = None
    name: str
    abbreviation: Optional[str] = None  # e.g., "LAL" for Los Angeles Lakers.
    city: Optional[str] = None
    conference: Optional[str] = None
    division: Optional[str] = None

# ---------------------------
# Players Payload
# ---------------------------
class PlayerPayload(BaseModel):
    id: Optional[int] = None
    name: str
    team_id: int                   # References Teams.id.
    position: Optional[str] = None  # e.g., "PG", "SG", etc.
    details: Optional[str] = None   # JSON or free-form text for additional metadata.

# ---------------------------
# Games Payload
# ---------------------------
class GamePayload(BaseModel):
    id: Optional[int] = None
    game_date: datetime.datetime  # The date and time of the game.
    home_team_id: int             # References Teams.id.
    away_team_id: int             # References Teams.id.
    venue: Optional[str] = None
    status: Optional[str] = Field(default="scheduled")  # e.g., "scheduled", "in-progress", "finished"

# ---------------------------
# PlayerStats Payload
# ---------------------------
class PlayerStatPayload(BaseModel):
    id: Optional[int] = None
    game_id: int                  # References Games.id.
    player_id: int                # References Players.id.
    stat_type: str                # e.g., "points", "rebounds", "assists".
    value: float                  # Stat value (e.g., 25 points).
    minutes_played: Optional[float] = None  # Minutes played in the game.
    additional_info: Optional[str] = None   # Optional JSON blob for extra stats (e.g., shooting splits).

# ---------------------------
# Odds Payload
# ---------------------------
class OddsPayload(BaseModel):
    id: Optional[int] = None
    game_id: int                  # References Games.id.
    player_id: Optional[int] = None  # Nullable for team-level odds.
    book_id: int                  # References Books.id.
    bet_type: str                 # e.g., "O/U", "moneyline", "prop".
    stat: Optional[str] = None    # Which statistic this bet concerns (e.g., "points").
    threshold: Optional[float] = None  # Threshold value for O/U bets, if applicable.
    odds_value: float             # Odds in decimal or American format.
    timestamp: Optional[datetime.datetime] = Field(default_factory=datetime.datetime.utcnow)
    additional_details: Optional[str] = None  # JSON for extra context (e.g., handicap details).

# ---------------------------
# Predictions Payload
# ---------------------------
class PredictionPayload(BaseModel):
    id: Optional[int] = None
    game_id: int                  # References Games.id.
    player_id: int                # References Players.id.
    stat: str                     # The stat being predicted, e.g., "points".
    predicted_value: float        # Model’s prediction.
    variance: Optional[float] = None  # Variance in the prediction.
    model_used: Optional[str] = None  # Identifier for the model/algorithm used.
    confidence: float             # Confidence score (0 to 1).
    timestamp: Optional[datetime.datetime] = Field(default_factory=datetime.datetime.utcnow)

# ---------------------------
# BetPicks Payload
# ---------------------------
class BetPickPayload(BaseModel):
    id: Optional[int] = None
    game_id: int                  # References Games.id.
    player_id: int                # References Players.id.
    bet_type: str                 # e.g., "O/U", "moneyline", "prop".
    suggestion: str               # Textual description (e.g., "bet over 30.5 points").
    recommended_amount: Optional[float] = None  # Suggested bet amount.
    expected_return: Optional[float] = None     # Calculated expected profit.
    predicted_value: float        # Model’s predicted value for reference.
    odds_value: float             # Current odds from a book for cross-checking.
    timestamp: Optional[datetime.datetime] = Field(default_factory=datetime.datetime.utcnow)

# ---------------------------
# InjuryReports Payload
# ---------------------------
class InjuryReportPayload(BaseModel):
    id: Optional[int] = None
    player_id: int                # References Players.id.
    report: str                   # Full text of the injury report.
    article_url: Optional[HttpUrl] = None  # Link to the source article.
    summary: str                  # Short summary of the injury impact.
    expected_impact: Optional[str] = None  # e.g., "increased minutes" or "limited play".
    timestamp: Optional[datetime.datetime] = Field(default_factory=datetime.datetime.utcnow)

# ---------------------------
# ScrapeLogs Payload
# ---------------------------
class ScrapeLogPayload(BaseModel):
    id: Optional[int] = None
    source: str                   # e.g., "Bet365 API", "PrizePicks".
    url: Optional[HttpUrl] = None   # URL that was scraped.
    scrape_time: Optional[datetime.datetime] = Field(default_factory=datetime.datetime.utcnow)
    status: Optional[str] = None  # "success" or "fail".
    error_message: Optional[str] = None  # Error details if any.

# ---------------------------
# UserAccounts Payload
# ---------------------------
class UserAccountPayload(BaseModel):
    id: Optional[int] = None
    username: str                 # Unique username.
    email: str                    # Unique email address.
    hashed_password: str          # Securely hashed password.
    created_at: Optional[datetime.datetime] = Field(default_factory=datetime.datetime.utcnow)
    account_type: Optional[str] = Field(default="standard")  # e.g., "admin", "standard".
    linked_accounts: Optional[str] = None  # JSON blob to store external account info.

#TODO: Add more models for other variables in the future.