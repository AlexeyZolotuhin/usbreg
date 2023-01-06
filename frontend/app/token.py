from flask import request, make_response, url_for
from flask import flash
from requests.structures import CaseInsensitiveDict


# вызывается в том случае если получен код 401 при запросе какой-либо страницы после авторизации
# т.е. когда истек срок токена. Также используется при выходе пользователя по кнопке Logout
def token_401(msg=""):
    if msg != "":
        flash(msg, 'error_login')
    res = make_response('', 301)
    res.headers['Location'] = url_for('auth.login')
    res.set_cookie("username", "", max_age=0)
    res.set_cookie("token", "", max_age=0)
    return res


def make_token_headers():
    if request.cookies.get('token'):
        headers = CaseInsensitiveDict()
        headers["Accept"] = "application/json"
        headers["Authorization"] = f"Bearer {request.cookies.get('token')}"
        return headers
    else:
        token_401()

