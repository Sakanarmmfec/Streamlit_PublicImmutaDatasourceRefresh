import streamlit as st
import requests

# Set the common headers
headers = {
    'accept': 'application/json',
    'Authorization': 'Bearer 6f4c9c20b94942bdaaf037e6e49ac316',  # Replace with your actual Bearer token
}

# Step 1: Run first API to get IDs with dynamic searchText
def get_ids_from_project_api(search_text):
    url = f'https://ia752ap7x16zab1jww8gh1gc4j.hosted.immutacloud.com/project?offset=0&size=100&sortOrder=asc&searchText={search_text}'
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()  # Parse the JSON response
        # Extract 'id' from the 'hits' list in the response
        ids = [item['id'] for item in data.get('hits', [])]  
        return ids, data  # Return both ids and the full response for display
    else:
        st.error(f"Error: {response.status_code}")
        return [], None

# Step 2: Run second API for each ID to get schemaEvolutionId
def get_schema_evolution_ids(ids):
    schema_evolution_ids = []
    all_responses = []  # To store responses for display
    
    for project_id in ids:
        url = f'https://ia752ap7x16zab1jww8gh1gc4j.hosted.immutacloud.com/project/{project_id}?checkForSqlAccount=true'
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            schema_evolution_id = data.get('schemaEvolutionId')
            if schema_evolution_id:
                schema_evolution_ids.append(schema_evolution_id)
            all_responses.append(data)  # Store the response
        else:
            st.error(f"Error for project {project_id}: {response.status_code}")
            all_responses.append({"error": f"Error for project {project_id}: {response.status_code}"})
    
    return schema_evolution_ids, all_responses

# Step 3: Run third API for each schemaEvolutionId
def detect_remote_changes(schema_evolution_ids):
    responses = []
    
    for schema_evolution_id in schema_evolution_ids:
        url = 'https://ia752ap7x16zab1jww8gh1gc4j.hosted.immutacloud.com/dataSource/detectRemoteChanges'
        data = {
            "schemaEvolutionId": schema_evolution_id,
            "skipColumnDetection": False
        }
        response = requests.put(url, json=data, headers=headers)
        
        if response.status_code == 200:
            responses.append(f"Successfully detected changes for schemaEvolutionId: {schema_evolution_id}")
        else:
            responses.append(f"Error for schemaEvolutionId {schema_evolution_id}: {response.status_code}")
    
    return responses

# Streamlit UI
st.title('Run Immuta API Refresh')

# Input field for search_text
search_text = st.text_input('Enter Dataset Name', '')

# Button to run the process
if st.button('Run'):
    if search_text:
        # Step 1: Get IDs
        ids, first_response = get_ids_from_project_api(search_text)
        if not ids:
            st.warning("No IDs found. Exiting.")
        else:
            # Display first API response
            st.subheader('Detect Project ID')
            st.json(first_response)  # Show the full response for the first API

            # Step 2: Get schemaEvolutionIds
            schema_evolution_ids, second_response = get_schema_evolution_ids(ids)
            if not schema_evolution_ids:
                st.warning("No schemaEvolutionIds found. Exiting.")
            else:
                # Display second API response
                st.subheader('Detect schemaEvolutionId')
                st.write(second_response)  # Show responses for the second API

                # Step 3: Detect remote changes for all schemaEvolutionIds
                final_responses = detect_remote_changes(schema_evolution_ids)
                
                # Display final responses
                st.subheader('Refresh Dataset')
                st.write(final_responses)  # Show the final result of the detection step
                
    else:
        st.warning("Please enter a search text.")
