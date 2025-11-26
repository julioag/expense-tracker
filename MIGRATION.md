# Migration to Vercel and Supabase

This guide outlines the steps to deploy the Expense Tracker application to Vercel and connect it to a Supabase database.

## Prerequisites

- A [Vercel](https://vercel.com/) account.
- A [Supabase](https://supabase.com/) account and project.
- [Vercel CLI](https://vercel.com/docs/cli) installed (optional, for local deployment).

## 1. Database Setup (Supabase)

1.  **Get Connection String**:
    - Go to your Supabase project settings.
    - Navigate to **Database** -> **Connect**.
    - Select **Transaction Pooler** (recommended for serverless environments like Vercel).
    - Copy the connection string (URI). It should look like `postgres://[user]:[password]@[host]:[port]/[dbname]?pgbouncer=true`.
    - **Important**: Replace `[password]` with your actual database password.

2.  **Import Data** (If applicable):
    - If you have a database export, use a tool like `psql` or a GUI client (e.g., TablePlus, DBeaver) to import the data into your Supabase database using the connection string.

3.  **Run Migrations** (Optional/Future Updates):
    - To apply schema changes (migrations) to your production database, run Alembic locally pointing to the production URL.
    - **Command**:
        ```bash
        # Set the DATABASE_URL environment variable to your Supabase connection string
        export DATABASE_URL="postgres://[user]:[password]@[host]:[port]/[dbname]?pgbouncer=true"
        
        # Run the migration
        alembic upgrade head
        ```
    - **Note**: Ensure you are in the `app` directory (or wherever `alembic.ini` is located) when running this command. Since `alembic.ini` is in `app/`, you should `cd app` first.

## 2. Vercel Deployment

1.  **Import Project**:
    - Go to your Vercel dashboard.
    - Click **Add New...** -> **Project**.
    - Import your `expense-tracker` repository.

2.  **Configure Project**:
    - **Framework Preset**: Select **Other** (or leave as detected if it picks up Python/FastAPI, but usually "Other" is fine with `vercel.json`).
    - **Root Directory**: `./` (default).

3.  **Environment Variables**:
    - Add the following environment variables in the Vercel project settings:
        - `DATABASE_URL`: Your Supabase connection string (from Step 1).
        - `API_KEY`: A strong secret key for your API authentication.
        - `ENVIRONMENT`: `production`

4.  **Deploy**:
    - Click **Deploy**.
    - Wait for the build to complete.

## 3. Verification

1.  **Check Health**:
    - Visit `https://your-project-name.vercel.app/health`. You should see `{"status": "healthy"}`.
2.  **Check Docs**:
    - Visit `https://your-project-name.vercel.app/docs` to see the Swagger UI.
3.  **Test API**:
    - Try making a request (e.g., to `/categories`) using your `x-api-key` header.

## Troubleshooting

- **Database Connection Issues**: Ensure you are using the **Transaction Pooler** connection string (port 6543) and that your password is correct.
- **Build Errors**: Check the Vercel build logs. Ensure `requirements.txt` is present and correct.
