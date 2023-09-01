from social_media.mimic.ok.flows.abstractokflow import AbstractOkFlow
from social_media.mimic.ok.requests.group.getinfo import GroupGetInfoRequest, GroupGetInfoResponse, GroupInfoItem
from social_media.mimic.ok.requests.url.getinfo import UrlGetInfoRequest, UrlGetInfoResponse


class OkGroupFlow(AbstractOkFlow):
    """
    Ok group flow for group-related requests
    """

    async def resolve_group_uid(self, group_url: str) -> str:
        """
        Resolve group UID by URL
        @param group_url:
        @return:
        """
        url_info_request = UrlGetInfoRequest(group_url)
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
