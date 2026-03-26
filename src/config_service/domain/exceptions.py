class InvalidYamlError(Exception):
    pass


class ValidationError(Exception):
    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        super().__init__(str(errors))


class ConfigurationNotFoundError(Exception):
    pass


class DuplicateVersionError(Exception):
    pass
