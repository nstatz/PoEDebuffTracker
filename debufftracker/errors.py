class ConfigError(Exception):
    """
    Dummy class that might be used later. Implement dummy class to prevent unnecessary refactoring
    """
    pass


class ColorConfigError(ConfigError):
    """
    Exception class that can be raised if invalid colors are used
    """
    def __init__(self, color):
        self.color = color

    def __str__(self):
        return f"{self.color} as colormethod not allowed. Check comments in config file"


class StatusConfigError(ConfigError):
    """
    Exception class that can be raised if invalid status config is used (ailment, curse, ground)
    """
    def __init__(self, problem_string):
        self.problem_string = problem_string

    def __str__(self):
        return f"""Problem with status config occured: {self.problem_string}"""

class FileConfigError(ConfigError):
    """
    Exception class that can be raised if invalid colors are used
    """
    def __init__(self, file_path):
        self.file_path = file_path

    def __str__(self):
        return f"{self.file_path} not found"