# bookclub_api.py
import os
import requests
from typing import Dict, List, Optional, Union, Any

class APIError(Exception):
    """Raised when there's an error communicating with the API."""
    pass

class ResourceNotFoundError(APIError):
    """Raised when the requested resource doesn't exist."""
    pass

class ValidationError(APIError):
    """Raised when the API rejects the request due to invalid data."""
    pass

class AuthenticationError(APIError):
    """Raised when there's an authentication issue."""
    pass

class BookClubAPI:
    """SDK for interacting with Book Club API powered by Supabase Edge Functions."""
    
    def __init__(self, base_url: str, api_key: str):
        """
        Initialize the Book Club API client.
        
        Args:
            base_url: The base URL for the Supabase project (e.g., 'https://your-project.supabase.co')
            api_key: The Supabase API key for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.functions_url = f"{self.base_url}/functions/v1"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
    
    def _handle_request_error(self, error: requests.exceptions.RequestException, resource_type: str, resource_id: Optional[str] = None) -> None:
        """
        Handle request errors and raise appropriate custom exceptions.
        
        Args:
            error: The original request exception
            resource_type: The type of resource being accessed (e.g., 'club', 'member')
            resource_id: The ID of the resource, if applicable
            
        Raises:
            ResourceNotFoundError: If the resource was not found (404)
            ValidationError: If the request was invalid (400)
            AuthenticationError: If there was an authentication issue (401, 403)
            APIError: For other API errors
        """
        if isinstance(error, requests.exceptions.HTTPError):
            status_code = error.response.status_code
            error_text = error.response.text
            
            if status_code == 404:
                id_info = f" with ID '{resource_id}'" if resource_id else ""
                raise ResourceNotFoundError(
                    f"{resource_type.capitalize()}{id_info} not found. "
                    f"Check if it exists in this environment."
                ) from error
            
            elif status_code == 400:
                raise ValidationError(f"Invalid request: {error_text}") from error
            
            elif status_code in (401, 403):
                raise AuthenticationError(f"Authentication error: {error_text}") from error
            
            else:
                raise APIError(f"API error ({status_code}): {error_text}") from error
        
        elif isinstance(error, requests.exceptions.ConnectionError):
            raise APIError(f"Connection error: Could not connect to the API. "
                          f"Check if the server is running and the URL is correct.") from error
        
        else:
            raise APIError(f"Request failed: {str(error)}") from error
    
    # Club Methods
    def get_club(self, club_id: str) -> Dict:
        """
        Get details for a specific club.
        
        Args:
            club_id: The ID of the club to retrieve
            
        Returns:
            Dict containing club details including members and active session
            
        Raises:
            ResourceNotFoundError: If the club doesn't exist
            AuthenticationError: If there's an authentication issue
            APIError: For other API errors
        """
        url = f"{self.functions_url}/club"
        params = {"id": club_id}
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self._handle_request_error(e, "club", club_id)
    
    def create_club(self, club_data: Dict) -> Dict:
        """
        Create a new club with all its associated data.
        
        Args:
            club_data: Dict containing club data including members and active session
            
        Returns:
            Dict containing success status and message
            
        Raises:
            ValidationError: If the club data is invalid
            AuthenticationError: If there's an authentication issue
            APIError: For other API errors
        """
        url = f"{self.functions_url}/club"
        
        try:
            response = requests.post(url, headers=self.headers, json=club_data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self._handle_request_error(e, "club")
    
    def update_club(self, club_id: str, name: str) -> Dict:
        """
        Update the name of a club.
        
        Args:
            club_id: The ID of the club to update
            name: The new name for the club
            
        Returns:
            Dict containing success status and message
            
        Raises:
            ResourceNotFoundError: If the club doesn't exist
            ValidationError: If the club data is invalid
            AuthenticationError: If there's an authentication issue
            APIError: For other API errors
        """
        url = f"{self.functions_url}/club"
        data = {
            "id": club_id,
            "name": name
        }
        
        try:
            response = requests.put(url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self._handle_request_error(e, "club", club_id)
    
    def delete_club(self, club_id: str) -> Dict:
        """
        Delete a club and all associated data.
        
        Args:
            club_id: The ID of the club to delete
            
        Returns:
            Dict containing success status and message
            
        Raises:
            ResourceNotFoundError: If the club doesn't exist
            AuthenticationError: If there's an authentication issue
            APIError: For other API errors
        """
        url = f"{self.functions_url}/club"
        params = {"id": club_id}
        
        try:
            response = requests.delete(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self._handle_request_error(e, "club", club_id)
    
    # Member Methods
    def get_member(self, member_id: int) -> Dict:
        """
        Get details for a specific member.
        
        Args:
            member_id: The ID of the member to retrieve
            
        Returns:
            Dict containing member details
            
        Raises:
            ResourceNotFoundError: If the member doesn't exist
            AuthenticationError: If there's an authentication issue
            APIError: For other API errors
        """
        url = f"{self.functions_url}/member"
        params = {"id": member_id}
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self._handle_request_error(e, "member", str(member_id))
    
    def create_member(self, member_data: Dict) -> Dict:
        """
        Create a new member.
        
        Args:
            member_data: Dict containing member data including name, points, etc.
            
        Returns:
            Dict containing success status and message
            
        Raises:
            ValidationError: If the member data is invalid
            AuthenticationError: If there's an authentication issue
            APIError: For other API errors
        """
        url = f"{self.functions_url}/member"
        
        try:
            response = requests.post(url, headers=self.headers, json=member_data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self._handle_request_error(e, "member")
    
    def update_member(self, member_id: int, update_data: Dict) -> Dict:
        """
        Update member details.
        
        Args:
            member_id: The ID of the member to update
            update_data: Dict containing fields to update (name, points, clubs, etc.)
            
        Returns:
            Dict containing success status and message
            
        Raises:
            ResourceNotFoundError: If the member doesn't exist
            ValidationError: If the member data is invalid
            AuthenticationError: If there's an authentication issue
            APIError: For other API errors
        """
        url = f"{self.functions_url}/member"
        data = {"id": member_id, **update_data}
        
        try:
            response = requests.put(url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self._handle_request_error(e, "member", str(member_id))
    
    def delete_member(self, member_id: int) -> Dict:
        """
        Delete a member.
        
        Args:
            member_id: The ID of the member to delete
            
        Returns:
            Dict containing success status and message
            
        Raises:
            ResourceNotFoundError: If the member doesn't exist
            AuthenticationError: If there's an authentication issue
            APIError: For other API errors
        """
        url = f"{self.functions_url}/member"
        params = {"id": member_id}
        
        try:
            response = requests.delete(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self._handle_request_error(e, "member", str(member_id))
    
    # Session Methods
    def get_session(self, session_id: str) -> Dict:
        """
        Get details for a specific session.
        
        Args:
            session_id: The ID of the session to retrieve
            
        Returns:
            Dict containing session details including book and discussions
            
        Raises:
            ResourceNotFoundError: If the session doesn't exist
            AuthenticationError: If there's an authentication issue
            APIError: For other API errors
        """
        url = f"{self.functions_url}/session"
        params = {"id": session_id}
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self._handle_request_error(e, "session", session_id)
    
    def create_session(self, session_data: Dict) -> Dict:
        """
        Create a new reading session.
        
        Args:
            session_data: Dict containing session data
            
        Returns:
            Dict containing success status and message
            
        Raises:
            ValidationError: If the session data is invalid
            AuthenticationError: If there's an authentication issue
            APIError: For other API errors
        """
        url = f"{self.functions_url}/session"
        
        try:
            response = requests.post(url, headers=self.headers, json=session_data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self._handle_request_error(e, "session")
    
    def update_session(self, session_id: str, update_data: Dict) -> Dict:
        """
        Update session details.
        
        Args:
            session_id: The ID of the session to update
            update_data: Dict containing fields to update
            
        Returns:
            Dict containing success status and message
            
        Raises:
            ResourceNotFoundError: If the session doesn't exist
            ValidationError: If the session data is invalid
            AuthenticationError: If there's an authentication issue
            APIError: For other API errors
        """
        url = f"{self.functions_url}/session"
        data = {"id": session_id, **update_data}
        
        try:
            response = requests.put(url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self._handle_request_error(e, "session", session_id)
    
    def delete_session(self, session_id: str) -> Dict:
        """
        Delete a session.
        
        Args:
            session_id: The ID of the session to delete
            
        Returns:
            Dict containing success status and message
            
        Raises:
            ResourceNotFoundError: If the session doesn't exist
            AuthenticationError: If there's an authentication issue
            APIError: For other API errors
        """
        url = f"{self.functions_url}/session"
        params = {"id": session_id}
        
        try:
            response = requests.delete(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self._handle_request_error(e, "session", session_id)


# Example usage
if __name__ == "__main__":
    # Initialize the API client
    api = BookClubAPI(
        base_url=os.getenv("SUPABASE_URL", "http://localhost:54321"),
        api_key=os.getenv("SUPABASE_KEY", "your-local-anon-key")
    )
    
    try:
        # Get club details
        club = api.get_club("club-1")
        print(f"Club name: {club['name']}")
        print(f"Number of members: {len(club['members'])}")
    except ResourceNotFoundError as e:
        print(f"Resource not found: {e}")
    except ValidationError as e:
        print(f"Validation error: {e}")
    except AuthenticationError as e:
        print(f"Authentication error: {e}")
    except APIError as e:
        print(f"API error: {e}")