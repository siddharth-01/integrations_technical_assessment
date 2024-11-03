# Project Description: VectorShift Integrations Technical Assessment

This project is an implementation for the VectorShift Integrations Technical Assessment. The goal was to integrate HubSpot OAuth authentication and data retrieval into an existing integrations framework, which also supports Notion and AirTable. The project involved both backend and frontend development using Python/FastAPI for server-side code and JavaScript/React for client-side functionalities.

### Key Features:
1. **HubSpot OAuth Integration**:
   - Developed `authorize_hubspot`, `oauth2callback_hubspot`, and `get_hubspot_credentials` functions in `hubspot.py` for the backend.
   - Implemented the OAuth flow to handle secure user authentication with HubSpot.

2. **Frontend Integration**:
   - Created `hubspot.js` in the `/frontend/src/integrations` directory.
   - Integrated the HubSpot component into the UI, ensuring seamless access alongside existing Notion and AirTable integrations.

3. **HubSpot Item Retrieval**:
   - Completed the `get_items_hubspot` function to query relevant HubSpot API endpoints and return a list of `IntegrationItem` objects.
   - Selected key data points from HubSpot, following patterns used in the existing Notion and AirTable integrations.

### Technical Stack:
- **Backend**: Python, FastAPI
- **Frontend**: JavaScript, React
- **Additional Services**: Redis for caching and state management

### Project Setup and Running Instructions

#### Backend
1. Navigate to the `/backend` directory.
2. Run the following commands:
   ```bash
   uvicorn main:app --reload
   ```
3. Ensure that `redis-server` is running for complete functionality.

#### Frontend
1. Navigate to the `/frontend` directory.
2. Install the necessary packages:
   ```bash
   npm i
   ```
3. Start the development server:
   ```bash
   npm run start
   ```

### Usage Instructions:
- Follow the prompts to initiate the HubSpot OAuth flow and authorize access.
- After authentication, utilize the provided UI to query HubSpot data and display results.
- Review and test `IntegrationItem` output via console logs.

### Testing Notes:
- Testing the integration required generating a new client ID and secret for HubSpot.
- AirTable and Notion integrations provided as references had redacted client data, so similar test credentials may be necessary.

### Conclusion:
This project showcases seamless integration with HubSpot, extending the existing integrations framework to support robust OAuth workflows and data retrieval processes.

---
Thank you for reviewing this implementation. If there are any questions or further customizations needed, feel free to reach out!

