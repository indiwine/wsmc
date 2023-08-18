import dataclasses
from typing import Type

from social_media.mimic.ok.requests.abstractrequest import GenericRequest, GenericResponse, RESPONSE_BODY, \
    AbstractResponse, AbstractRequestParams, GenericResponseBody


@dataclasses.dataclass
class GetInfoParams(AbstractRequestParams):
    uids: str
    move_to_top: bool = True
    fields: str = 'product_create_allowed,video_tab_hidden,join_allowed,edit_apps_allowed,blocked,members_count,end_date,photo_id,add_paid_theme_allowed,invite_free_allowed,has_daily_photo,start_date,catalog_create_allowed,group_photo.pic_base,subcategory,group.cover_buttons,call_allowed,mentions_subscription,name,group_photo.album_id,user_paid_content_till,phone,paid_access_price,category,messages_allowed,products_tab_hidden,user_paid_content,add_theme_allowed,manage_messaging_allowed,user_paid_access_till,invite_allowed,paid_content_price,description,location_longitude,promo_theme_allowed,publish_delayed_theme_allowed,access_type,advanced_publication_allowed,create_ads_allowed,group_photo.offset,paid_access,graduate_year,product_create_zero_lifetime_allowed,created_ms,feed_subscription,country,gos_org,group.cover_series,followers_count,business,homepage_url,manage_members,leave_allowed,edit_allowed,has_group_agreement,suggest_theme_allowed,user_paid_access,group.mobile_cover,ads_manager_allowed,admin_id,content_as_official,location_latitude,disable_reason,view_paid_themes_allowed,age_restricted,group_photo.id,group_challenge_create_allowed,mentions_subscription_allowed,product_create_suggested_allowed,stats_allowed,uid,main_photo,role,paid_content,private,notifications_subscription,profile_buttons,request_sent,messaging_allowed,unfollow_allowed,daily_photo_post_allowed,address,min_age,paid_content_description,reshare_allowed,premium,city,group.status,follow_allowed,transfers_allowed,group_news,group_journal_allowed,group_photo.standard_height,paid_access_description,group_photo.standard_width'

    def to_execute_dict(self) -> dict:
        return dataclasses.asdict(self)


class GetInfoResponseBody(GenericResponseBody):
    uid: str
    name: str
    created_ms: int
    photo_id: str
    main_photo: dict
    attrs: dict
    members_count: int
    premium: bool
    private: bool
    gos_org: bool
    paid_access: str
    paid_content: str
    access_type: str
    category: str
    city: str
    subcategory: str
    address: str
    phone: str
    homepage_url: str
    feed_subscription: bool
    notifications_subscription: bool
    mentions_subscription: bool
    revenue_pp_enabled: bool
    video_tab_hidden: bool
    products_tab_hidden: bool
    messages_allowed: bool
    content_as_official: bool
    cover: dict
    mobile_cover: dict
    profile_buttons: dict
    pin_notifications_off: bool
    has_group_agreement: bool
    has_daily_photo: bool
    has_unseen_daily_photo: bool

class GetInfoResponse(GenericResponse):
    @staticmethod
    def get_body_class() -> Type[RESPONSE_BODY]:
        return GetInfoResponseBody

class GetInfoRequest(GenericRequest):
    def __init__(self, group_id: str):
        params = GetInfoParams(group_id)

        super().__init__('group', 'getInfo', params)

    @staticmethod
    def bound_response_cls() -> Type[AbstractResponse]:
        return GetInfoResponse
