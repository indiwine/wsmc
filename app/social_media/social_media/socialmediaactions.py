from enum import Enum


class SocialMediaActions(Enum):
    """
    Enum for social media actions
    Represents the actions that can be performed on social media
    """
    LOGIN = 'login'
    PROFILE = 'profile'
    POSTS = 'posts'
    GROUP = 'group'
    UNKNOWN_PROFILES = 'unknown_profiles'
    PROFILES_DISCOVERY = 'profiles_discovery'
