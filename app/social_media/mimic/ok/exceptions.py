from enum import Enum
import logging

logger = logging.getLogger(__name__)

class OkErrorCodes(Enum):
    UNKNOWN: int = 1
    SERVICE: int = 2
    METHOD: int = 3
    REQUEST: int = 4
    ACTION_BLOCKED: int = 7
    FLOOD_BLOCKED: int = 8
    IP_BLOCKED: int = 9
    PERMISSION_DENIED: int = 10
    LIMIT_REACHED: int = 11
    CANCELLED: int = 12
    NOT_MULTIPART: int = 21
    NOT_ACTIVATED: int = 22
    NOT_YET_INVOLVED: int = 23
    NOT_OWNER: int = 24
    NOT_ACTIVE: int = 25
    TOTAL_LIMIT_REACHED: int = 26
    NETWORK: int = 30
    NETWORK_TIMEOUT: int = 31
    NOT_ADMIN: int = 50
    PARAM: int = 100
    PARAM_API_KEY: int = 101
    PARAM_SESSION_EXPIRED: int = 102
    PARAM_SESSION_KEY: int = 103
    PARAM_SIGNATURE: int = 104
    PARAM_RESIGNATURE: int = 105
    PARAM_ENTITY_ID: int = 106
    PARAM_USER_ID: int = 110
    PARAM_ALBUM_ID: int = 120
    PARAM_PHOTO_ID: int = 121
    PARAM_WIDGET: int = 130
    PARAM_MESSAGE_ID: int = 140
    PARAM_COMMENT_ID: int = 141
    PARAM_HAPPENING_ID: int = 150
    PARAM_HAPPENING_PHOTO_ID: int = 151
    PARAM_GROUP_ID: int = 160
    PARAM_PERMISSION: int = 200
    PARAM_APPLICATION_DISABLED: int = 210
    PARAM_DECISION: int = 211
    PARAM_BADGE_ID: int = 212
    PARAM_PRESENT_ID: int = 213
    PARAM_RELATION_TYPE: int = 214
    PARAM_FIELDSET: int = 220
    NOT_FOUND: int = 300
    EDIT_PHOTO_FILE: int = 324
    AUTH_LOGIN: int = 401
    AUTH_LOGIN_CAPTCHA: int = 402
    AUTH_LOGIN_WEB_HUMAN_CHECK: int = 403
    NOT_SESSION_METHOD: int = 451
    SESSION_REQUIRED: int = 453
    CENSOR_MATCH: int = 454
    FRIEND_RESTRICTION: int = 455
    GROUP_RESTRICTION: int = 456
    UNAUTHORIZED_RESTRICTION: int = 457
    PRIVACY_RESTRICTION: int = 458
    PHOTO_SIZE_LIMIT_EXCEEDED: int = 500
    PHOTO_SIZE_TOO_SMALL: int = 501
    PHOTO_SIZE_TOO_BIG: int = 502
    PHOTO_INVALID_FORMAT: int = 503
    PHOTO_IMAGE_CORRUPTED: int = 504
    PHOTO_NO_IMAGE: int = 505
    PHOTO_PIN_TOO_MUCH: int = 508
    IDS_BLOCKED: int = 511
    PHOTO_ALBUM_NOT_BELONGS_TO_USER: int = 512
    PHOTO_ALBUM_NOT_BELONGS_TO_GROUP: int = 513
    IDS_SESSION_VERIFICATION_REQUIRED: int = 514
    MEDIA_TOPIC_BLOCK_LIMIT: int = 600
    MEDIA_TOPIC_TEXT_LIMIT: int = 601
    MEDIA_TOPIC_POLL_QUESTION_TEXT_LIMIT: int = 602
    MEDIA_TOPIC_POLL_ANSWERS_LIMIT: int = 603
    MEDIA_TOPIC_POLL_ANSWER_TEXT_LIMIT: int = 604
    MEDIA_TOPIC_WITH_FRIENDS_LIMIT: int = 605
    MEDIA_TOPIC_WITH_FRIENDS_USER_LIMIT: int = 606
    MEDIA_TOPIC_LINK_BAD_FORMAT: int = 607
    GROUP_DUPLICATE_JOIN_REQUEST: int = 610
    COMMENT_NOT_FOUND: int = 700
    INVALID_AUTHOR: int = 701
    COMMENT_NOT_ACTIVE: int = 702
    TIMEOUT_EXCEEDED: int = 704
    CHAT_NOT_FOUND: int = 705
    MESSAGE_NOT_ACTIVE: int = 706
    STICKER_SERVICE_UNAVAILABLE_TO_USER: int = 707
    STICKER_MESSAGE_INVALID: int = 708
    GIF_SERVICE_UNAVAILABLE_TO_USER: int = 709
    CHAT_MAX_PARTICIPANT_COUNT_LIMIT: int = 800
    CHAT_PARTICIPANTS_EMPTY_BLOCKED_USERS: int = 801
    CHAT_PARTICIPANTS_EMPTY_NON_EXISTENT_USERS: int = 802
    NO_SUCH_APP: int = 900
    CALLBACK_INVALID_PAYMENT: int = 1001
    INVALID_PAYMENT: int = 1003
    DUPLICATE_PAYMENT: int = 1004
    NOT_ENOUGH_MONEY: int = 1005
    VCHAT_SERVICE_DISABLED: int = 1101
    TARGET_USER_UNAVAILABLE: int = 1102
    FRIENDSHIP_REQUIRED: int = 1103
    BATCH: int = 1200
    APP_NO_PLATFORM_ALLOWED: int = 1300
    APP_DEVICE_NOT_ALLOWED: int = 1301
    APP_DEVICE_NOT_SPECIFIED: int = 1302
    APP_EMPTY_SEARCH_PARAMS: int = 1400
    APP_SEARCH_SCENARIO_DOES_NOT_EXIST: int = 1401
    GRAPH_PARAM_REQUEST: int = 2001
    INVALID_RESPONSE: int = 5000
    SYSTEM: int = 9999


class OkApiCallException(Exception):
    ok_code: OkErrorCodes
    ok_data: dict | None

    def __init__(self, code: int, msg: str, data = None):
        super().__init__(msg)

        try:
            self.ok_code = OkErrorCodes(code)
        except ValueError:
            logger.warning(f'Unknown error code: {code}')
            self.ok_code = OkErrorCodes.UNKNOWN

        self.ok_data = data


class OkResponseNotFoundException(Exception):
    pass


