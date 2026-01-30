import requests
import streamlit as st
import os
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

class TrelloService:
    def __init__(self, api_key=None, token=None):
        self.api_key = api_key or os.getenv("TRELLO_API_KEY")
        self.token = token or os.getenv("TRELLO_TOKEN")
        self.base_url = "https://api.trello.com/1"

    def _get_auth_params(self):
        return {
            "key": self.api_key,
            "token": self.token
        }

    @st.cache_data(ttl=600, show_spinner="Coletando dados do Trello...")
    def get_board_data(_self, board_id):
        """Fetch all necessary board data in parallel-ish via API fields."""
        url = f"{_self.base_url}/boards/{board_id}"
        params = {
            **_self._get_auth_params(),
            "lists": "open",
            "cards": "visible",
            "members": "all",
            "labels": "all",
            "card_fields": "name,idList,idMembers,idLabels,due,dueComplete,dateLastActivity,url",
            "fields": "name,desc,url"
        }
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Erro na API do Trello: {e}")
            return None

    @st.cache_data(ttl=600)
    def get_actions(_self, board_id, limit=1000):
        url = f"{_self.base_url}/boards/{board_id}/actions"
        params = {
            **_self._get_auth_params(),
            "filter": "updateCard:idList,createCard",
            "limit": limit
        }
        try:
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            return response.json()
        except Exception:
            return []

    def validate_auth(self):
        url = f"{self.base_url}/members/me"
        try:
            res = requests.get(url, params=self._get_auth_params(), timeout=5)
            return res.status_code == 200
        except:
            return False
