class Log:
    """Thin wrapper around Django management command stdout/style."""

    def __init__(self, stdout=None, style=None):
        self._stdout = stdout
        self._style = style

    def __call__(self, msg: str) -> None:
        if self._stdout:
            self._stdout.write(msg)

    def success(self, msg: str) -> None:
        if self._stdout:
            self._stdout.write(self._style.SUCCESS(msg) if self._style else msg)

    def warning(self, msg: str) -> None:
        if self._stdout:
            self._stdout.write(self._style.WARNING(msg) if self._style else msg)

    def error(self, msg: str) -> None:
        if self._stdout:
            self._stdout.write(self._style.ERROR(msg) if self._style else msg)
