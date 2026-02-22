class MissingEnvVarError(ValueError):
    def __init__(self, var_name: str):
        message = f"Environment variable '{var_name}' is required but not set."
        super().__init__(message)
