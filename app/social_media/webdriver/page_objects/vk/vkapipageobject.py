import logging
from typing import List, Generator

from social_media.dtos import SmProfileDto
from .abstractvkpageobject import AbstractVkPageObject
from .api_objects.vkprofilenode import VkProfileNode
from ...common import chunks_list

logger = logging.getLogger(__name__)


class VkApiPageObject(AbstractVkPageObject):
    ACTIONS_PER_EXEC = 25
    VK_API_VER = '5.131'

    obtain_access_token_func = """
    """

    def bulk_users_get(
        self,
        oid_list: List[str],
        oid_per_request: int = 100
    ) -> Generator[List[SmProfileDto], None, None]:

        oid_chunks = list(chunks_list(oid_list, oid_per_request))

        for batch in chunks_list(oid_chunks, self.ACTIONS_PER_EXEC):
            yield from self.do_load_data_from_browser(batch)

    def do_load_data_from_browser(self, batch: List[List[str]]) -> Generator[List[SmProfileDto], None, None]:
        exec_code = self.generate_batch_user_get_codes(batch)
        logger.debug('Sending exec code to VK')
        raw_response: dict = self.driver.execute_async_script("""
            const url = 'https://api.vk.com/method/execute';
            const callback = arguments[arguments.length - 1];
            const code = arguments[0];
            const apiVersion = arguments[1];
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
            data.set('code', code);
            data.set('v', apiVersion);
            
            const req = new XMLHttpRequest();
            req.responseType = 'json';
            
            req.onload = () => {
                if ('error' in req.response) {
                    throw new Error(`Error while making Native API request: ${JSON.stringify(req.response, null, 4)}`);
                }
                
                callback(req.response)
            };
            req.onerror = ev => { 
                throw new Error('Error while making request') 
            };
            
            req.open('POST', url);
            req.send(data);
            """, exec_code, self.VK_API_VER)
        logger.debug('VK async exec done')

        for response_chunk in raw_response['response']:
            yield self.map_profile_node_to_dto(response_chunk)

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
