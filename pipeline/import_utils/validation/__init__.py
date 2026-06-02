"""Public entry points for import-set annotation validation.

Keep this module tiny so existing imports can continue to use
`from pipeline.import_utils.validation import validate_bit_meta` while the
implementation lives in focused validator modules.
"""

from .validator import validate_bit_meta

__all__ = ["validate_bit_meta"]
