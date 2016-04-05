class MissingSAMLMetadataException(Exception):
    """
    This exception is thrown when 'DB' is used but metadata is not set in DB
    """
    def __init__(self,  msg):
        self.msg = msg

    def __str__(self):
        return self.msg
