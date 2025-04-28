from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.db import close_old_connections
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from urllib.parse import parse_qs
from django.contrib.auth import get_user_model

User = get_user_model()

@database_sync_to_async
def get_user_from_token(token_key):
    """Get user from JWT token"""
    try:
        # Verify token
        token = AccessToken(token_key)
        user_id = token.payload.get('user_id')
        
        # Get user
        return User.objects.get(id=user_id)
    except (InvalidToken, TokenError, User.DoesNotExist):
        return AnonymousUser()

class TokenAuthMiddleware(BaseMiddleware):
    """Custom middleware for token-based WebSocket authentication"""
    
    async def __call__(self, scope, receive, send):
        # Close database connections to prevent them being reused across threads
        close_old_connections()
        
        # Get token from query string
        query_string = parse_qs(scope['query_string'].decode())
        token = query_string.get('token', [None])[0]
        
        if token:
            # Get user from token
            scope['user'] = await get_user_from_token(token)
        else:
            scope['user'] = AnonymousUser()
        
        return await super().__call__(scope, receive, send)

def TokenAuthMiddlewareStack(inner):
    """Convenience wrapper for adding TokenAuthMiddleware to a list of middleware"""
    return TokenAuthMiddleware(inner)