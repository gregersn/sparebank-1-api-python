class APIError(Exception):
    status_code: int
    error: str

    def __init__(self, status_code: int, error: str):
        self.status_code = status_code
        self.error = error
        super().__init__(f"API Error {status_code}: {error}")
