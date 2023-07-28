from http import HTTPStatus

from rest_framework.test import APIClient

from .base_testing_class import BaseTestingClass


class GenericEndpointTests(BaseTestingClass):
    ACTIONS = ('list', 'create', 'retireve',
               'update', 'partial_update', 'destroy')
    allowed_actions: tuple[str] | None = None
    not_allowed_actions: tuple[str] | None = None
    endpoint: str | None = None
    payload: dict | None = None

    class Meta:
        abstract = True

    def _set_actions(self):
        def get_actions(actions):
            return tuple(set(self.ACTIONS) - set(actions))
        assert not (self.allowed_actions is None
                    and self.not_allowed_actions is None)
        if self.allowed_actions is None:
            self.allowed_actions = get_actions(self.not_allowed_actions)
        else:
            self.not_allowed_actions = get_actions(self.allowed_actions)

    def _is_allowed(self, action: str) -> None:
        self._set_actions()
        assert action in self.allowed_actions

    def set_current_action(self, action: str):
        self._is_allowed(action)
        return action

    def get_payload(self):
        return self.payload.copy()

    def query(self, client: APIClient, action: str,
              *, path_param: int = 1, payload: dict | None = None):
        detailed_url = f'{self.endpoint}{path_param}/'
        match action.lower():
            case 'list':
                return client.get(self.endpoint)
            case 'create':
                return client.post(self.endpoint, data=payload)
            case 'retrieve':
                return client.get(detailed_url)
            case 'update':
                return client.put(detailed_url, data=payload)
            case 'partial_update':
                return client.patch(detailed_url, data=payload)
            case 'destroy':
                return client.delete(detailed_url)

    def test_not_allowed_actions(self, auth_client):
        self._set_actions()
        for action in self.not_allowed_actions:
            response = self.query(auth_client, action)
            assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED
