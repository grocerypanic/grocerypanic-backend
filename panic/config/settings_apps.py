"""Custom settings for individual apps."""

# appengine

WARM_UP_DATABASE_WAIT_INTERVAL = 0.5

# kitchen

PAGINATION_OVERRIDE_PARAM = "all_results"
TRANSACTION_HISTORY_MAX = 14
LEGACY_TRANSACTION_HISTORY_UPPER_BOUND = 150

# spa_security

BLEACH_RESTORE_LIST = {"&amp;": "&"}

# utilities

TOCTREE_FACTORY_SETTINGS = 'root.toctree.settings'
