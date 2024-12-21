# Movie Recommendation Service

Welcome! This service enhances the experience for movie enthusiasts by providing robust and innovative tools for film recommendations. Let’s dive into the details!

<br>

## **Project Idea**
The core idea of this project is to improve the quality of movie recommendation searches.

<br>

## **Features Provided to Users**

### 1. Registration
Users can choose their preferred registration method:
- **Via Google Email:** A simple and familiar option for many users.
- **Full Registration (Sign-Up):** Users can register using any email. A confirmation code will be sent to their email, which they need to verify on the website.

### 2. Login
Registered users can log in using their email and password or via the Google service, depending on their chosen registration method.

### 3. Reviews (Posts)
Users can share their thoughts and recommendations:
- **Create Posts:** Users can write posts with relevant tags.
- **Like Posts:** Quality recommendations can be promoted by liking posts.
- **Comment:** Users can leave comments on posts.

### 4. Tagging System
Every post must include a tag. Tags help other users find recommendations for specific movies or actors, provided posts with such tags exist. There is also a tag sorting feature that allows users to distinguish whether tags are related to the movie theme or not.

(**Green** indicates correct items, **red** indicates incorrect ones)

### 5. Platform Recommendation System
The service provides a dedicated recommendation system:
1. **Choose a Criterion:** Users start by selecting a criterion for recommendations.
2. **Follow Guidance:** Users create their "wishlist" following on-site prompts.
3. **Receive Recommendations:** A curated list of recommended movies, complete with posters and essential information, is presented to the user.

### 6. Error Notifications
If an error occurs while using the website, users will be notified via a pop-up window with details about the error type.

### 7. Logging
Logs are used to track all user actions on the website. They are stored in the database. In case of an error, it will be possible to trace user actions and address service issues.

<br>

## **Running the Service**

### Required Applications
To run the service, you will need the following tools:
- Docker
- Docker Compose
- Git

### Steps to Launch

1. **Clone the Project:**

   First, clone the project repository using the following command:
   ```bash
   git clone git@github.com:PletkaDaniil/WEB_Project.git
   ```

2. **Build and Start the Containers:**

   Next, build and start the containers using:
   ```bash
   docker-compose up --build app
   ```
3. **Shut Down Containers:**

   To stop the containers, use:
   ```bash
   docker-compose down
   ```

4. **Start the Application:**

   After building the containers, to start the application, run:
   ```bash
   docker-compose up app
   ```
5. **Stop the Application:**

   To stop the application, use:
   ```bash
   docker-compose down
   ```
* **Tests:**

   After building the containers, to start tests, run:
   ```bash
      docker-compose run tests
   ```
---
<br>


## **XML**

To view the technical specification formatted in XML, go to the `dtd` folder and open it in your browser, or [use a link](https://codebeautify.org/xmlviewer) with better visualization (simply insert the [technical_specification.xml](dtd/technical_specification.xml) file there).

---

<br>

## **ER Diagram**

The diagram is implemented in the [Diagram.drawio](Diagram.drawio).

To view it, open the [Draw.io](https://www.drawio.com/) website and insert the file.

![ER diagram of the domain model](images/Diagram.png)

---


<br>

## Project Explanation

1.  **How to set up the poster functionality?**

You need to visit [the website](https://www.omdbapi.com). Select "API Key" from the top menu and complete the registration process.

![OMDB](images/OMDB.png)

After registration, you will receive an email containing the API key. Insert this key into the [user_server.json](app/website/user_server.json) file.

```bash
   {
    "user":{
            ...
            "api_key": "your_key"
        }
   }
```

---

2.  **How to log in using Google Mail?**

Here’s [an example guide](https://www.youtube.com/watch?v=FKgJEfrhU1E&t=392s) on how to complete all the steps in Google Cloud and obtain a [client_secret.json](app/website/client_secret.json)  file as a result:

```bash
   {
    "web":{
        "client_id":"",
        "project_id":"",
        "auth_uri":"",
        "token_uri":"",
        "auth_provider_x509_cert_url":"",
        "client_secret":"",
        "redirect_uris":[""]
      }
   }
```
---

3.  **How to send a confirmation code to any email in the sign_up section?**

First, choose the Google account to which you will link this functionality.
Enable two-factor authentication on your account.
Then, go to the App Passwords section and generate your app password.

![OMDB](images/App_passwords.png)


Update the [user_server.json](app/website/user_server.json) file with your information.

```bash
   {
    "user":
        {
            "MAIL_USERNAME": "your_email@gmail.com",
            "MAIL_PASSWORD": "your_password",
            "MAIL_DEFAULT_SENDER": "your_email@gmail.com",
            ...
        }
   }
```

---

<br>

## **API/UI**


### _GET Routes_ :

#### **GET** `/login`
- **Description**: Displays the login page for users.
- **Process**: The user is presented with a form to enter their email and password. This is the initial page for logging into the system.
- **Response**: Renders an HTML login form.

#### **GET** `/login/google`
- **Description**: Initiates the Google OAuth authentication process.
- **Process**: The user is redirected to the Google login page. After successful login, OAuth will redirect the user back to the `/callback` route.
- **Response**: Redirects the user to Google for authentication.

#### **GET** `/callback`
- **Description**: Handles the callback from Google OAuth and finalizes the authentication process.
- **Process**: After the user logs in through Google, the system extracts the user’s information and stores it. If the user is new, they will be added to the database.
- **Response**: Redirects the user to the homepage or profile page.

#### **GET** `/logout`
- **Description**: Ends the current user session.
- **Process**: Removes session data and redirects the user to the homepage.
- **Response**: Redirects to the homepage.

#### **GET** `/home`
- **Description**: Displays the main feed of posts.
- **Process**: The user can view all available posts sorted by the number of likes or other criteria.
- **Response**: Renders an HTML page with the list of posts.

#### **GET** `/create-post`
- **Description**: Displays a form for creating a new post.
- **Process**: The user is shown a form to input the title, description, and other details for the new post.
- **Response**: Renders an HTML form for entering post details.

#### **GET** `/delete-post/<id>`
- **Description**: Deletes a post with the given ID.
- **Process**: The user is prompted to confirm the deletion of the post.
- **Response**: Redirects to the main feed with the updated list of posts.

#### **GET** `/posts/<username>`
- **Description**: Displays all posts from a specific user.
- **Process**: Only posts from the user with the given username are shown.
- **Response**: Renders an HTML page displaying the user’s posts.

---

###  _POST Routes_ :

#### **POST** `/login`
- **Description**: Handles user login.
- **Process**: When the user submits their login form with email and password, the system checks the credentials and logs the user in if they are correct.
- **Response**: Redirects the user to the homepage or the dashboard if login is successful.

#### **POST** `/create-post`
- **Description**: Creates a new post.
- **Process**: The user submits a form with the post details, such as title, description, and associated movie information.
- **Response**: Redirects the user back to the homepage with the new post displayed in the feed.

#### **POST** `/delete-post/<id>`
- **Description**: Deletes a post.
- **Process**: The system removes the post with the given ID from the database.
- **Response**: Redirects to the homepage with the updated list of posts.


---
This project is designed to provide a seamless and interactive movie recommendation experience for all users. Enjoy exploring and discovering great films!