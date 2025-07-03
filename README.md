# Project Repository

This is the initial README file for the project.

## Email/Gmail Integration Setup

Your backend supports outgoing email reminders (Resend API) and Gmail OAuth2 connection for users.  
To enable these features, you **must** register for API keys at both Resend and Google and add them to your `.env` file.

### Resend setup (Email Reminders)

1. Visit https://resend.com/ and sign up.
2. Navigate to *API Keys*, create one.
3. Copy the API key and add to your `.env`:

    ```
    RESEND_API_KEY="your_resend_api_key"
    ```

### Gmail OAuth2 setup (Google Cloud)

1. Visit [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create a new OAuth2 Client ID for "Web application".
3. Set the *redirect URI* to:
   ```
   https://<your-backend-domain>/email/gmail/oauth-callback
   ```
   (Set both backend and frontend URIs if you use both in development.)
4. Note your *Client ID* and *Client Secret*. Add these to `.env`:
    ```
    GOOGLE_CLIENT_ID="your_client_id"
    GOOGLE_CLIENT_SECRET="your_client_secret"
    GOOGLE_OAUTH_REDIRECT_URI="your_callback_url"
    GOOGLE_AUTH_SCOPE="https://www.googleapis.com/auth/gmail.readonly"
    ```

### Environment Variable Security

- Do **not** commit the `.env` file.
- Store production environment variables using your cloud or Docker/CI secrets.

### More Info

- To view and test live API endpoints, open the FastAPI docs at `/docs` or redoc at `/redoc`
- For generated OpenAPI JSON (for frontend codegen/TypeScript types), use `/docs/openapi`
- For self-test or deployment validation, see `/self-test` (returns {"status": "ok"} if backend config is valid)
- See `/email/setup-help` for runtime credential setup instructions
