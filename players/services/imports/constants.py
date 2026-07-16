"""Constants used by the player import workflow."""

SOURCE_MEMBER_LIST = "vcb_member_list_csv"
SOURCE_ROSTER_DETAIL = "vcb_roster_detail_csv"
SOURCE_MANUAL_STAFF = "manual_staff_csv"

SOURCE_CHOICES = [
    (SOURCE_MEMBER_LIST, "VCB member list CSV"),
    (SOURCE_ROSTER_DETAIL, "VCB roster detail CSV"),
    (SOURCE_MANUAL_STAFF, "Manual staff CSV"),
]

MAX_CSV_UPLOAD_BYTES = 5 * 1024 * 1024
MAX_CSV_ROWS = 5000

MAPPING_KEY_PROVISION_PLAYER_ACCOUNTS = "_provision_player_accounts"
MAPPING_KEY_ACTIVATE_PLAYER_ACCOUNTS = "_activate_player_accounts"

ACTION_CREATE = "create"
ACTION_UPDATE = "update"
ACTION_NEEDS_REVIEW = "needs_review"
ACTION_SKIP = "skip"
ACTION_ERROR = "error"

RESOLUTION_ACTION_COMMIT = "commit"
RESOLUTION_ACTION_CREATE_NEW = "create_new"
RESOLUTION_ACTION_USE_CANDIDATE = "use_candidate"
RESOLUTION_KEEP_EXISTING = "keep_existing"
RESOLUTION_USE_IMPORTED = "use_imported"
RESOLUTION_METADATA_ONLY = "metadata_only"

PLAYER_FIELD_KEYS = [
    "first_name",
    "last_name",
    "preferred_name",
    "birthdate",
    "birth_year",
    "gender",
    "division",
    "team_name",
    "primary_positions",
    "bats",
    "throws",
    "school",
    "graduation_year",
]

PERMANENT_PLAYER_FIELD_KEYS = [
    "first_name",
    "last_name",
    "preferred_name",
    "birthdate",
    "birth_year",
    "gender",
    "primary_positions",
    "bats",
    "throws",
    "school",
    "graduation_year",
]

CONFLICT_FIELDS = [
    "first_name",
    "last_name",
    "preferred_name",
    "birthdate",
    "birth_year",
    "gender",
    "primary_positions",
    "bats",
    "throws",
    "school",
    "graduation_year",
]

IDENTIFIER_FIELD_TYPES = {
    "registration_id": "registration_id",
    "registrant_id": "registrant_id",
    "team_id": "team_id",
    "source_player_id": "source_player_id",
}

HEADER_ALIASES = {
    "first_name": {
        "first",
        "first name",
        "firstname",
        "given name",
        "player first name",
    },
    "last_name": {
        "last",
        "last name",
        "lastname",
        "surname",
        "family name",
        "player last name",
    },
    "full_name": {"name", "full name", "player", "player name"},
    "preferred_name": {"preferred", "preferred name", "nickname", "nick name"},
    "birthdate": {"birthdate", "birth date", "date of birth", "dob"},
    "birth_year": {"birth year", "year of birth", "yob"},
    "gender": {"gender", "sex"},
    "division": {"division", "level", "program"},
    "team_name": {"team", "team name", "current team"},
    "roster_status": {"roster status", "status", "membership status"},
    "jersey_number": {"jersey", "jersey number", "number", "uniform number"},
    "membership_start_date": {
        "membership start date",
        "start date",
        "starts on",
        "roster start",
    },
    "membership_end_date": {"membership end date", "end date", "ends on", "roster end"},
    "roster_source_id": {"roster source id", "membership id", "roster id"},
    "primary_positions": {
        "position",
        "positions",
        "primary position",
        "primary positions",
    },
    "bats": {"bats", "batting", "hits"},
    "throws": {"throws", "throwing"},
    "school": {"school"},
    "graduation_year": {"graduation year", "grad year", "class year"},
    "registration_id": {"registration id", "registration", "reg id"},
    "registrant_id": {"registrant id", "member id", "participant id"},
    "team_id": {"team id", "teamid"},
    "source_player_id": {"player id", "source player id", "external player id"},
}
