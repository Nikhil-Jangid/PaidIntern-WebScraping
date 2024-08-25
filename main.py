import streamlit as st
import requests
from bs4 import BeautifulSoup

def scrape_doctors(location, specialization, page=1):
    url = f"https://www.practo.com/{location}/{specialization}?page={page}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return f"Unable to access the website. Error: {e}", []

    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract the total number of doctors
    count_element = soup.find('div', class_='u-d-flex flex-ai-center u-spacer--top-md')
    total_count = count_element.get_text(strip=True) if count_element else "No data found"

    # Extract details of each doctor
    doctor_list = []
    for doctor in soup.find_all('div', class_='listing-doctor-card'):
        name = doctor.find('h2', class_='doctor-name')
        specialty = doctor.find('div', class_='u-grey_3-text')
        rating = doctor.find('a', class_='uv2-spacer--md-right')

        doctor_list.append({
            'name': name.get_text(strip=True) if name else 'N/A',
            'specialty': specialty.get_text(strip=True) if specialty else 'N/A',
            'rating': rating.get_text(strip=True) if rating else 'N/A',
        })

    # Determine if there are more pages
    next_button = soup.find('a', class_='c-next-btn')
    has_more_pages = next_button is not None

    return total_count, doctor_list, has_more_pages

# Streamlit app
st.title("Practo Doctor Profile Viewer")

# User inputs
location = st.text_input("Enter the location (e.g., Bangalore)")
specialization = st.selectbox(
    "Select specialization", 
    ["General-Physician", "Dentist", "Gynecologist", "Pediatrician", "Orthopedic"]
)

# Initialize session state for profile navigation
if 'current_profile' not in st.session_state:
    st.session_state.current_profile = 0
if 'all_doctors' not in st.session_state:
    st.session_state.all_doctors = []
if 'total_count' not in st.session_state:
    st.session_state.total_count = ""
if 'page' not in st.session_state:
    st.session_state.page = 1

# Scrape button
if st.button("Scrape"):
    if location and specialization:
        with st.spinner('Scraping data...'):
            all_doctors = []
            page = 1  # Start from the first page
            total_count = None
            while True:
                count, doctors, has_more_pages = scrape_doctors(location, specialization, page)
                if total_count is None:
                    total_count = count
                all_doctors.extend(doctors)
                if not has_more_pages:
                    break
                page += 1

            st.session_state.all_doctors = all_doctors
            st.session_state.total_count = total_count
            st.session_state.current_profile = 0  # Reset to the first profile

            st.success(f"Total number of doctors available: {total_count}")
            st.success("Here are the Top 10 Rcommended Doctors for you.")

if st.session_state.all_doctors:
    # Show current profile
    doctor = st.session_state.all_doctors[st.session_state.current_profile]
    st.write(f"**Name:** {doctor['name']}")
    st.write(f"**Specialty:** {doctor['specialty']}")
    st.write(f"**Rating:** {doctor['rating']}")
    st.write("---")

    # Navigation buttons
    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if st.session_state.current_profile >= 1:
            if st.button("Previous"):
                st.session_state.current_profile -= 1

    with col2:
        st.write(f"Profile {st.session_state.current_profile + 1} of {len(st.session_state.all_doctors)}")

    with col3:
        if st.session_state.current_profile < len(st.session_state.all_doctors) - 1:
            if st.button("Next"):
                st.session_state.current_profile += 1

else:
    st.error("No doctor details found. Please check the location and specialization and try again.")
