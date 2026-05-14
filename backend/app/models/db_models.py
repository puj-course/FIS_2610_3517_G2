"""
Modelos SQLAlchemy para las tablas de PostgreSQL.
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.core.database import Base


class MatchDB(Base):
    __tablename__ = "matches"

    id = Column(String(50), primary_key=True)
    player_home_id = Column(String(50), nullable=False)
    player_home_name = Column(String(100), nullable=False)
    player_home_country = Column(String(10), nullable=False)
    player_home_ranking = Column(Integer, nullable=True)
    player_away_id = Column(String(50), nullable=False)
    player_away_name = Column(String(100), nullable=False)
    player_away_country = Column(String(10), nullable=False)
    player_away_ranking = Column(Integer, nullable=True)
    tournament_id = Column(String(50), nullable=False)
    tournament_name = Column(String(100), nullable=False)
    tournament_surface = Column(String(20), nullable=False)
    tournament_category = Column(String(20), nullable=False)
    tournament_location = Column(String(100), nullable=False)
    date = Column(DateTime, nullable=False)
    status = Column(String(20), nullable=False, default="upcoming")
    score = Column(String(50), nullable=True)


class CombinationDB(Base):
    __tablename__ = "combinations"

    id = Column(String(50), primary_key=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    selections = relationship("SelectionDB", back_populates="combination",
                              cascade="all, delete-orphan")


class SelectionDB(Base):
    __tablename__ = "selections"

    id = Column(String(50), primary_key=True)
    combination_id = Column(String(50), ForeignKey("combinations.id", ondelete="CASCADE"),
                            nullable=False)
    match_id = Column(String(50), nullable=False)
    player_home_name = Column(String(100), nullable=False)
    player_away_name = Column(String(100), nullable=False)
    tournament_name = Column(String(100), nullable=False)
    match_date = Column(DateTime, nullable=False)
    added_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    combination = relationship("CombinationDB", back_populates="selections")


class PlayerStatsDB(Base):
    __tablename__ = "player_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(String(50), nullable=False, unique=True)
    player_name = Column(String(100), nullable=False)
    overall_win_rate = Column(Float, nullable=False, default=50.0)
    clay_win_rate = Column(Float, nullable=False, default=50.0)
    hard_win_rate = Column(Float, nullable=False, default=50.0)
    grass_win_rate = Column(Float, nullable=False, default=50.0)
    recent_form = Column(Text, nullable=True)
    recent_win_rate = Column(Float, nullable=False, default=50.0)
    total_matches = Column(Integer, nullable=False, default=0)
    titles = Column(Integer, nullable=False, default=0)


class HeadToHeadDB(Base):
    __tablename__ = "head_to_head"

    id = Column(Integer, primary_key=True, autoincrement=True)
    player1_id = Column(String(50), nullable=False)
    player2_id = Column(String(50), nullable=False)
    player1_wins = Column(Integer, nullable=False, default=0)
    player2_wins = Column(Integer, nullable=False, default=0)
    total_matches = Column(Integer, nullable=False, default=0)
    last_matches = Column(Text, nullable=True)
