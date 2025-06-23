# Flutter Earth: Google Earth Engine Service Account Setup Guide

This guide provides step-by-step instructions for setting up a Google Cloud Platform (GCP) **Service Account**, which is the recommended method for authenticating with Google Earth Engine when using the Flutter Earth application.

## Why Use a Service Account?

-   **No Browser Needed**: Service accounts authenticate automatically without requiring you to log in through a browser, making them ideal for desktop applications and automated scripts.
-   **Secure**: You grant specific permissions to the service account, limiting its access to only what is necessary.
-   **Stable**: Unlike user-based authentication, service account credentials do not expire as frequently.

---

## Step 1: Sign up for Earth Engine Access

If you have not already, you must register your Google account for Earth Engine access.
1.  Go to the [Earth Engine signup page](https://signup.earthengine.google.com/).
2.  Follow the instructions to register. Approval can sometimes take a day or two.
3.  You will receive an email once your account is activated. **You cannot proceed until your registration is approved.**

---

## Step 2: Create a Google Cloud Project

All Earth Engine usage is managed through a Google Cloud Project.
1.  Navigate to the [Google Cloud Console](https://console.cloud.google.com/).
2.  Click the project selector dropdown in the top bar and click **"New Project"**.
3.  Enter a descriptive **Project name** (e.g., "Flutter Earth GEE Project").
4.  Select a **Location** if applicable and click **"Create"**.

---

## Step 3: Enable the Earth Engine API

You must enable the Earth Engine API for your new project.
1.  With your new project selected in the Google Cloud Console, navigate to the **"APIs & Services"** > **"Library"**.
2.  In the search bar, type `Earth Engine API` and press Enter.
3.  Click on the **"Earth Engine API"** result.
4.  Click the **"Enable"** button. If it is already enabled, you don't need to do anything.

---

## Step 4: Create a Service Account

Now, we will create the service account that Flutter Earth will use to authenticate.
1.  In the Google Cloud Console, navigate to **"IAM & Admin"** > **"Service Accounts"**.
2.  Click **"+ CREATE SERVICE ACCOUNT"** at the top.
3.  **Service account details**:
    -   **Service account name**: Give it a clear name, like `flutter-earth-user`.
    -   The **Service account ID** will be generated for you.
    -   **Description**: Add a description, such as "Service account for the Flutter Earth desktop application".
4.  Click **"CREATE AND CONTINUE"**.
5.  **Grant this service account access to project**:
    -   Click the **Role** dropdown.
    -   Search for and select the **"Earth Engine Resource Viewer"** role. This provides sufficient permissions for downloading data.
    -   *Note: If you plan to manage assets, you may need a more permissive role like "Earth Engine Resource Writer".*
6.  Click **"CONTINUE"**.
7.  Leave the "Grant users access to this service account" section blank and click **"DONE"**.

---

## Step 5: Create and Download a JSON Key

The service account needs a key file for authentication.
1.  You should now see your newly created service account in the list.
2.  Click the three-dot "Actions" menu (⋮) at the far right of your service account's row and select **"Manage keys"**.
3.  Click **"ADD KEY"** > **"Create new key"**.
4.  Select **JSON** as the key type and click **"CREATE"**.
5.  A JSON file will be automatically downloaded to your computer. **This is your service account key.**

**IMPORTANT:**
-   **Treat this JSON file like a password.** Do not share it or commit it to version control.
-   Store it in a secure, memorable location on your computer (e.g., in a `.keys` folder in your user home directory).
-   Flutter Earth will ask you for the path to this file, but it will not store the file's contents.

---

## Step 6: Configure Flutter Earth

The final step is to tell Flutter Earth how to use your new credentials. The application now automatically handles this through its authentication setup.

1.  Launch the Flutter Earth application (`python main.py`).
2.  The application will automatically look for authentication details. If not found, it will guide you to set them up.
3.  You will need two pieces of information:
    -   **Your GCP Project ID**: The ID of the project you created in Step 2.
    -   **Path to your Service Account Key**: The full path to the JSON file you downloaded in Step 5.
4.  The application will test the connection and save the configuration for future use.

You are now ready to use Flutter Earth! 