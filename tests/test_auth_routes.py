# pokedex_project/tests/test_auth_routes.py
from flask import url_for
from models import User


def test_signup_page_loads(client, app):
    with app.app_context():
        signup_url = url_for('auth.signup')
    response = client.get(signup_url)
    assert response.status_code == 200
    html_content = response.data.decode('utf-8')  # Decode first
    assert "Create your Pokédex Account" in html_content  # Assert against the string


def test_login_page_loads(client, app):
    with app.app_context():
        login_url = url_for('auth.login')
    response = client.get(login_url)
    assert response.status_code == 200
    html_content = response.data.decode('utf-8')  # Decode first
    assert "Login to Pokédex" in html_content  # Assert against the string


# Using init_database for a clean slate
def test_successful_signup_and_login(client, app, init_database):
    # Signup
    with app.app_context():
        signup_url = url_for('auth.signup')
        login_url = url_for('auth.login')
        index_url = url_for('main.index')

        response = client.post(signup_url, data=dict(
            username='newuser',
            email='new@example.com',
            password='newpassword',
            confirm_password='newpassword'
        ), follow_redirects=True)
    assert response.status_code == 200
    html_content = response.data.decode('utf-8')  # DECODE here
    assert "Congratulations, you are now a registered user!" in html_content

    # Check user in DB
    with app.app_context():
        user = User.query.filter_by(username='newuser').first()
        assert user is not None
        assert user.email == 'new@example.com'

    # Login
    response = client.post(login_url, data=dict(
        identifier='newuser',  # or new@example.com
        password='newpassword'
    ), follow_redirects=True)
    assert response.status_code == 200
    html_content = response.data.decode('utf-8')
    assert "Welcome back, newuser!" in html_content
    assert index_url in response.request.path  # Check if it landed on index page
    # ---- ADD THIS DEBUG BLOCK ----
    print("\n--- DEBUG: Searching for navbar content in test_successful_signup_and_login ---")
    # 'user' variable from earlier in this test function is the 'newuser' object
    profile_link_text = f"{user.username}'s Profile"
    if profile_link_text in html_content:
        print(f"Found '{profile_link_text}' in html_content.")
    else:
        print(f"DID NOT FIND '{profile_link_text}' in html_content.")
        # Try to print the navbar section to see what's actually there
        # This specific class is part of the div containing the auth links in base.html
        nav_links_container_start = html_content.find(
            '<div class="flex items-center space-x-4">')
        if nav_links_container_start != -1:
            # Try to find the end of this specific div or its parent nav
            # This is a rough way to get a snippet; adjust if needed
            snippet_end = html_content.find(
                '</nav>', nav_links_container_start)
            if snippet_end != -1:
                print("NAVBAR LINKS HTML SNIPPET:\n",
                      html_content[nav_links_container_start: snippet_end])
            else:
                print("Could not find end of nav tag for snippet.")
        else:
            print("Could not find start of navbar links container for snippet.")
    # ---- END DEBUG BLOCK ----
    # Check navbar reflects logged in user
    assert "newuser's Profile" in html_content


def test_logout(auth_client, app):  # auth_client is already logged in as 'testuser'
    with app.app_context():
        logout_url = url_for('auth.logout')
        index_url = url_for('main.index')

    response = auth_client.get(logout_url, follow_redirects=True)
    assert response.status_code == 200
    html_content = response.data.decode('utf-8')
    assert "You have been logged out." in html_content
    assert index_url in response.request.path
    assert "Login" in html_content
    assert "testuser's Profile" not in html_content
