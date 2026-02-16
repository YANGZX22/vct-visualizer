"""
Utility functions for VCT Display Demo
"""
import os
from config import IMAGES_DIR, TEAMS_BY_REGION, TEAM_NAME_MAPPING


def normalize_team_name(team_name):
    """Normalize team name to abbreviation"""
    team_lower = team_name.strip().lower()
    # Check direct mapping first
    if team_lower in TEAM_NAME_MAPPING:
        return TEAM_NAME_MAPPING[team_lower]
    # Check if already an abbreviation
    for region, teams in TEAMS_BY_REGION.items():
        if team_lower in teams:
            return team_lower
    # Return original if no mapping found
    return team_lower


def get_team_icon_path(team_name):
    """Get the icon path for a team"""
    team_lower = normalize_team_name(team_name)
    for region, teams in TEAMS_BY_REGION.items():
        if team_lower in teams:
            return os.path.join(IMAGES_DIR, region, f"{team_lower}.png")
    return None


def get_tournament_icon_path(tournament_name):
    """Get the icon path for a tournament"""
    name = tournament_name.lower()
    # Handle mapping for amer -> americas
    if name == "amer":
        name = "americas"
    # Check for png first, then jpg
    png_path = os.path.join(IMAGES_DIR, "vct", f"{name}.png")
    if os.path.exists(png_path):
        return png_path
    jpg_path = os.path.join(IMAGES_DIR, "vct", f"{name}.jpg")
    if os.path.exists(jpg_path):
        return jpg_path
    return png_path  # Return png path as default


def get_card_background_path(tournament_name):
    """Get the card background image path for a tournament"""
    name = tournament_name.lower()
    # Map tournament names to card filenames
    if name == "amer":
        name = "americas"
    return os.path.join(IMAGES_DIR, "card", f"{name}_card.png")
