import dataclasses
import logging
from typing import List, Generator

from social_media.dtos import SmProfileDto
from .abstractvkpageobject import AbstractVkPageObject
from .api_objects.vkprofilenode import VkProfileNode
from ...common import chunks_list
from ...exceptions import WsmcWebDriverNativeApiCallTimout

logger = logging.getLogger(__name__)

VK_API_VER = '5.131'


@dataclasses.dataclass
class VkNativeApiRequest:
    method: str
    payload: dict
    api_version: str = VK_API_VER


class VkApiPageObject(AbstractVkPageObject):
    ACTIONS_PER_EXEC = 25

    obtain_access_token_func = """
    """

    def bulk_users_get(
        self,
        oid_list: List[str],
        oid_per_request: int = 100
    ) -> Generator[List[SmProfileDto], None, None]:

        oid_chunks = list(chunks_list(oid_list, oid_per_request))

        for batch in chunks_list(oid_chunks, self.ACTIONS_PER_EXEC):
            yield from self.do_bulk_users_get(batch)

    def friends_get(self, user_oid: int) -> Generator[List[SmProfileDto], None, None]:
        yield from self.do_friends_get(user_oid)

    def do_bulk_users_get(self, batch: List[List[str]]) -> Generator[List[SmProfileDto], None, None]:
        logger.debug('Sending exec code to VK')
        native_api_request = VkNativeApiRequest(
            method='execute',
            payload={
                'code': self.generate_batch_user_get_codes(batch)
            }
        )

        raw_response: dict = self.make_native_api_request(native_api_request)
        logger.debug('VK async exec done')
        if 'error' in raw_response and raw_response['error'] == 'timeout':
            raise WsmcWebDriverNativeApiCallTimout('Call for profiles has been timed out')

        for response_chunk in raw_response['response']:
            yield self.map_profile_node_to_dto(response_chunk)

    def do_friends_get(self, user_oid: int, limit: int = 5000) -> Generator[List[SmProfileDto], None, None]:
        request_payload = {
            'user_id': user_oid,
            'fields': 'nickname,contacts',
            'count': limit,
            'offset': 0
        }

        native_api_request = VkNativeApiRequest(
            method='friends.get',
            payload=request_payload
        )

        total_friends = None

        while True:
            raw_response = self.make_native_api_request(native_api_request)
            response = raw_response['response']
            if total_friends is None:
                total_friends = response['count']

            users = response['items']
            num_of_users = len(users)

            yield self.map_profile_node_to_dto(users)

            if num_of_users == limit:
                request_payload['offset'] += limit

            if num_of_users < limit:
                break

    def make_native_api_request(self, request):
        return self.driver.execute_async_script("""
            const callback = arguments[arguments.length - 1];
            const apiRequestModel = arguments[0];
            const payload = apiRequestModel.payload;
            
            const url = `https://api.vk.com/method/${apiRequestModel.method}`;
            
            const currentOid = window.curNotifier.uid;
            
            const obtainAccessToken = () => {
                const regex = /:web_token:login:auth$/;
                const storageKeys = Object.keys(localStorage).filter(key => regex.test(key))
                
                for (key of storageKeys) {
                    const rawData = localStorage.getItem(key);
                    console.log(rawData)
                    if (!rawData) {
                        continue;
                    }
                    
                    const authObj = JSON.parse(rawData);
                    if ('user_id' in authObj && 'access_token' in authObj && authObj.user_id === currentOid) {
                        return authObj.access_token;
                    }
                }
                throw Error('access_token cannot be obtained');
            }
            
            const data = new FormData();
            data.set('access_token', obtainAccessToken())
            Object.keys(payload).forEach(formKey => data.set(formKey, payload[formKey]))
            data.set('v', apiRequestModel.api_version);
            
            const req = new XMLHttpRequest();
            req.responseType = 'json';
            
            const timeoutCb = () => callback({ error: 'timeout' })
            
            const timer = setTimeout(timeoutCb, 100 * 1000);
            req.onload = () => {
                clearTimeout(timer);
                if ('error' in req.response) {
                    throw new Error(`Error while making Native API request: ${JSON.stringify(req.response, null, 4)}`);
                }
                
                callback(req.response)
            };
            
            req.onerror = ev => { 
                clearTimeout(timer);
                throw new ev;
            };
            
            req.ontimeout = ev => {
                clearTimeout(timer);
                timeoutCb();
            }
            
            req.onabort = ev => {
                clearTimeout(timer);
                timeoutCb();
            }
            
            req.open('POST', url);
            req.send(data);
            
            """, dataclasses.asdict(request))

    @classmethod
    def generate_batch_user_get_codes(cls, batch: List[List[str]]) -> str:
        user_get_calls = ",".join(map(lambda oids: cls.generate_user_get_code(oids), batch))
        return f'return [{user_get_calls}];'

    @staticmethod
    def map_profile_node_to_dto(profile_nodes: list) -> List[SmProfileDto]:
        return list(map(lambda raw_obj: VkProfileNode(raw_obj).to_dto(), profile_nodes))

    @staticmethod
    def generate_user_get_code(oid_list: List[str]) -> str:
        return f"""
        API.users.get({{
        'user_ids': '{",".join(oid_list)}', 
        'fields': 'bdate,connections,contacts,city,country,domain,home_town,site,maiden_name,universities'
        }})"""
