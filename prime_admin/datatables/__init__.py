from .student_records import (
    dt_registered_students,
    dt_examiners,
    dt_passers,
    dt_hired,
    dt_payments
)
from . import supplies_datatable
from . import fund_wallet_statement_datatable
from . import other_expenses_datatable
from .fund_wallet import (
    dt_utilities,
    dt_office_supplies
)
from .cash_flow import (
    dt_statements
)
from .batches import (
    dt_batches
)
from .branches import (
    dt_branches
)
from .cash_on_hand import (
    dt_student_payments,
    dt_items_sold,
    dt_accomodations
)
from .transactions import (
    dt_transactions
)
from .settings.examination import (
    dt_batch_numbers_settings,
    dt_sessions_settings,
    dt_industries_settings,
    dt_klts_settings,
    dt_venues_settings
)
from .settings import (
    dt_orientators_settings
)
from .pages import (
    dt_our_testimonies
)
