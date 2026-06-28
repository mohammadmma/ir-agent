class RetrievalConstraintError(Exception):
    """Base for any retrieval-policy violation raised by the guard."""


class BudgetExceededError(RetrievalConstraintError):
    """Raised when a request would exceed the configured API budget."""


class IllegalRequestError(RetrievalConstraintError):
    """Raised when a page is fetched before being discovered, or when it is
    outside the legal (en.tsv) page set."""