(function () {
    const method = 'friends.get'
    const url = `https://api.vk.com/method/${method}`;
    const callback = (res) => console.log('API call response', res) ;
    const payload = {
        'user_id': 169845376,
        'fields': 'nickname,contacts',
        'count': 100
    }
    const apiVersion = '5.131';
    const currentOid = window.curNotifier.uid;

    const obtainAccessToken = () => {
        const regex = /:web_token:login:auth$/;
        const storageKeys = Object.keys(localStorage).filter(key => regex.test(key))

        for (key of storageKeys) {
            const rawData = localStorage.getItem(key);
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
    data.set('v', apiVersion);
    Object.keys(payload).forEach(formKey => data.set(formKey, payload[formKey]))


    const req = new XMLHttpRequest();
    req.responseType = 'json';

    const timeoutCb = () => callback({error: 'timeout'})

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
})();