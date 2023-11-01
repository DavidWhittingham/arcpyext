# coding=utf-8
"""
This module contains an enumerated type representing ISO Topic Categories.
"""
from aenum import StrEnum


class TopicCategory(StrEnum):
    _init_ = "value standard_name display_name portal_name"

    BIOTA = "002", "biota", "Biota", "/Categories/Biota"
    BOUNDARIES = "003", "boundaries", "Boundaries", "/Categories/Boundaries"
    CLIMATOLOGY_METEOROLOGY_ATMOSPHERE = "004", "climatologyMeteorologyAtmosphere", "Climatology, meteorology, and atmosphere", "/Categories/Climatology, meteorology, and atmosphere"
    ECONOMY = "005", "economy", "Economy", "/Categories/Economy"
    ELEVATION = "006", "elevation", "Elevation", "/Categories/Elevation"
    ENVIRONMENT = "007", "environment", "Environment", "/Categories/Environment"
    FARMING = "001", "farming", "Farming", "/Categories/Farming"
    GEOSCIENTIFIC_INFORMATION = "008", "geoscientificInformation", "Geoscientific information", "/Categories/Geoscientific information"
    HEALTH = "009", "health", "Health", "/Categories/Health"
    IMAGERY_BASE_MAPS_EARTH_COVER = "010", "imageryBaseMapsEarthCover", "Imagery, basemaps, and Earth cover", "/Catagories/Imagery, basemaps, and Earth cover"
    INLAND_WATERS = "012", "inlandWaters", "Inland waters", "/Categories/Inland waters"
    INTELLIGENCE_MILITARY = "011", "intelligenceMilitary", "Intelligence and military", "/Categories/Intelligence and military"
    LOCATION = "013", "location", "Location", "/Categories/Location"
    OCEANS = "014", "oceans", "Oceans", "/Categories/Oceans"
    PLANNING_CADASTRE = "015", "planningCadastre", "Planning and cadastre", "/Categories/Planning and cadastre"
    SOCIETY = "016", "society", "Society", "/Categories/Society"
    STRUCTURE = "017", "structure", "Structure", "/Categories/Structure"
    TRANSPORTATION = "018", "transportation", "Transportation", "/Categories/Transportation"
    UTILITIES_COMMUNICATION = "019", "utilitiesCommunication", "Utilities and communication", "/Categories/Utilities and communication"