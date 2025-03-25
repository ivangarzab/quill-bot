import os
import requests
from typing import Dict, List, Optional, Union, Any

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
    
    def get_club(self, club_id: str) -> Dict:
        """
        Get details for a specific club.
        
        Args:
            club_id: The ID of the club to retrieve
            
        Returns:
            Dict containing club details including members and active session
        """
        url = f"{self.functions_url}/club"
        params = {"id": club_id}
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def create_club(self, club_data: Dict) -> Dict:
        """
        Create a new club with all its associated data.
        
        Args:
            club_data: Dict containing club data including members and active session
            
        Returns:
            Dict containing success status and message
        """
        url = f"{self.functions_url}/club"
        response = requests.post(url, headers=self.headers, json=club_data)
        response.raise_for_status()
        return response.json()
    
    def update_club(self, club_id: str, name: str) -> Dict:
        """
        Update the name of a club.
        
        Args:
            club_id: The ID of the club to update
            name: The new name for the club
            
        Returns:
            Dict containing success status and message
        """
        url = f"{self.functions_url}/club"
        data = {
            "id": club_id,
            "name": name
        }
        response = requests.put(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()
    
    def delete_club(self, club_id: str) -> Dict:
        """
        Delete a club and all associated data.
        
        Args:
            club_id: The ID of the club to delete
            
        Returns:
            Dict containing success status and message
        """
        url = f"{self.functions_url}/club"
        params = {"id": club_id}
        response = requests.delete(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_member(self, member_id: int) -> Dict:
        """
        Get details for a specific member.
        
        Args:
            member_id: The ID of the member to retrieve
            
        Returns:
            Dict containing member details
        """
        url = f"{self.functions_url}/member"
        params = {"id": member_id}
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def create_member(self, member_data: Dict) -> Dict:
        """
        Create a new member.
        
        Args:
            member_data: Dict containing member data including name, points, etc.
            
        Returns:
            Dict containing success status and message
        """
        url = f"{self.functions_url}/member"
        response = requests.post(url, headers=self.headers, json=member_data)
        response.raise_for_status()
        return response.json()
    
    def update_member(self, member_id: int, update_data: Dict) -> Dict:
        """
        Update member details.
        
        Args:
            member_id: The ID of the member to update
            update_data: Dict containing fields to update (name, points, clubs, etc.)
            
        Returns:
            Dict containing success status and message
        """
        url = f"{self.functions_url}/member"
        data = {"id": member_id, **update_data}
        response = requests.put(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()
    
    def delete_member(self, member_id: int) -> Dict:
        """
        Delete a member.
        
        Args:
            member_id: The ID of the member to delete
            
        Returns:
            Dict containing success status and message
        """
        url = f"{self.functions_url}/member"
        params = {"id": member_id}
        response = requests.delete(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_session(self, session_id: str) -> Dict:
        """
        Get details for a specific session.
        
        Args:
            session_id: The ID of the session to retrieve
            
        Returns:
            Dict containing session details including book and discussions
        """
        url = f"{self.functions_url}/session"
        params = {"id": session_id}
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def create_session(self, session_data: Dict) -> Dict:
        """
        Create a new reading session.
        
        Args:
            session_data: Dict containing session data
            
        Returns:
            Dict containing success status and message
        """
        url = f"{self.functions_url}/session"
        response = requests.post(url, headers=self.headers, json=session_data)
        response.raise_for_status()
        return response.json()
    
    def update_session(self, session_id: str, update_data: Dict) -> Dict:
        """
        Update session details.
        
        Args:
            session_id: The ID of the session to update
            update_data: Dict containing fields to update
            
        Returns:
            Dict containing success status and message
        """
        url = f"{self.functions_url}/session"
        data = {"id": session_id, **update_data}
        response = requests.put(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()
    
    def delete_session(self, session_id: str) -> Dict:
        """
        Delete a session.
        
        Args:
            session_id: The ID of the session to delete
            
        Returns:
            Dict containing success status and message
        """
        url = f"{self.functions_url}/session"
        params = {"id": session_id}
        response = requests.delete(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()


# Example usage
if __name__ == "__main__":
    # Initialize the API client
    api = BookClubAPI(
        base_url=os.getenv("SUPABASE_URL"),
        api_key=os.getenv("SUPABASE_KEY")
    )
    
    # Get club details
    club = api.get_club("club-1")
    print(f"Club name: {club['name']}")
    print(f"Number of members: {len(club['members'])}")