from social_media.mimic.ok.flows.abstractokflow import AbstractOkFlow
from social_media.mimic.ok.requests.group.getinfo import GroupGetInfoRequest, GroupGetInfoResponse, GroupInfoItem
from social_media.mimic.ok.requests.entities.user import UserItem
from social_media.mimic.ok.requests.url.getinfo import UrlGetInfoRequest, UrlGetInfoResponse
from social_media.mimic.ok.requests.users.getinfoby import UserGetInfoByRequest, UserGetInfoByResponse


class OkCommonFlow(AbstractOkFlow):
    """
    Ok group flow for group-related requests
    """

    async def resolve_url_to_uid(self, url: str) -> str:
        """
        Resolve UID by URL
        @param url:
        @return:
        """
        url_info_request = UrlGetInfoRequest(url)
        url_info_response: UrlGetInfoResponse = await self.perform_batch_request(
            'group.getInfo',
            url_info_request
        )

        return str(url_info_response.get_body().objectIdEncoded)


    async def fetch_group_info(self, group_uid: str) -> GroupInfoItem:
        """
        Fetch group info by group UID
        @param group_uid:
        @return:
        """
        group_info_request = GroupGetInfoRequest(group_uid)
        group_info_response: GroupGetInfoResponse = await self.perform_batch_request(
            'group.getInfo',
            group_info_request
        )

        return group_info_response.find_group_info(group_uid)


    async def fetch_user_info(self, uid: str) -> UserItem:
        """
        Fetch user info by user UID
        @param uid:
        @return:
        """
        user_info_request = UserGetInfoByRequest(uid)
        user_info_response: UserGetInfoByResponse = await self.perform_batch_request(
            'user.getInfoBy',
            user_info_request
        )

        return user_info_response.get_body().user
