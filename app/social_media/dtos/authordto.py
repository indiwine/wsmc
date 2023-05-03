from dataclasses import dataclass, field


@dataclass
class AuthorDto:
    """
    This class represents an author of whatever object it's attached to.
    Usually it should be a user or a group of a given social media
    """

    oid: str
    name: str
    url: str

    is_group: bool = field(metadata={'transient': True})
