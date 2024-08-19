class MerakiHealthCheckError(Exception):
    def __init__(self, message: str, category: str, severity: str):
        self.message = message
        self.category = category
        self.severity = severity
        super().__init__(self.message)

    def __str__(self):
        return f"{self.severity.upper()} - {self.category}: {self.message}"