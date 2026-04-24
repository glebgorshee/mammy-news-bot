"""
Клиент GigaChat API (Сбер).
OAuth 2.0 + chat completions. Бесплатный тариф для физлиц (GIGACHAT_API_PERS).
"""
import os
import time
import uuid
import logging
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

log = logging.getLogger("gigachat")

OAUTH_URL = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
API_BASE = "https://gigachat.devices.sberbank.ru/api/v1"


class GigaChatClient:
    def __init__(self, auth_key: str, scope: str = "GIGACHAT_API_PERS"):
        self.auth_key = auth_key
        self.scope = scope
        self._token: str | None = None
        self._expires_at: float = 0.0  # unix seconds

    def _refresh_token(self) -> None:
        r = requests.post(
            OAUTH_URL,
            headers={
                "Authorization": f"Basic {self.auth_key}",
                "RqUID": str(uuid.uuid4()),
                "Accept": "application/json",
            },
            data={"scope": self.scope},
            verify=False,
            timeout=30,
        )
        r.raise_for_status()
        j = r.json()
        self._token = j["access_token"]
        # expires_at приходит в миллисекундах
        self._expires_at = float(j["expires_at"]) / 1000.0
        log.info("GigaChat token refreshed, valid until %s", self._expires_at)

    def _ensure_token(self) -> None:
        # Рефрешим если нет токена или осталось меньше 60 сек до истечения
        if not self._token or time.time() > self._expires_at - 60:
            self._refresh_token()

    def chat(
        self,
        system: str,
        user: str,
        model: str = "GigaChat",
        max_tokens: int = 500,
        temperature: float = 0.3,
    ) -> str:
        self._ensure_token()
        r = requests.post(
            f"{API_BASE}/chat/completions",
            headers={
                "Authorization": f"Bearer {self._token}",
                "Accept": "application/json",
            },
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "temperature": temperature,
                "max_tokens": max_tokens,
            },
            verify=False,
            timeout=60,
        )
        r.raise_for_status()
        data = r.json()
        return data["choices"][0]["message"]["content"]


def get_client_from_env() -> GigaChatClient | None:
    """Возвращает клиент если есть GIGACHAT_CREDENTIALS, иначе None."""
    key = os.environ.get("GIGACHAT_CREDENTIALS")
    if not key:
        return None
    scope = os.environ.get("GIGACHAT_SCOPE", "GIGACHAT_API_PERS")
    return GigaChatClient(key, scope=scope)
