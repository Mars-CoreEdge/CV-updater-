# Supabase Authentication Setup Guide

## Overview
This application now includes beautiful login and signup pages with Supabase authentication. Follow these steps to set up authentication for your CV Updater application.

## Prerequisites
- A Supabase account (free tier available)
- Node.js and npm installed

## Setup Steps

### 1. Create a Supabase Project
1. Go to [supabase.com](https://supabase.com)
2. Sign up for a free account
3. Create a new project
4. Wait for the project to be set up (usually takes 2-3 minutes)

### 2. Get Your Supabase Credentials
1. In your Supabase dashboard, go to Settings > API
2. Copy your Project URL and anon public key
3. Update the `.env` file in the `frontend` directory:

```env
REACT_APP_SUPABASE_URL=https://your-project-id.supabase.co
REACT_APP_SUPABASE_ANON_KEY=your-anon-key-here
```

### 3. Configure Authentication Providers (Optional)
If you want to enable Google and GitHub login:

#### Google OAuth
1. Go to Authentication > Settings in your Supabase dashboard
2. Enable Google provider
3. Add your Google OAuth credentials
4. Set up authorized redirect URIs

#### GitHub OAuth
1. Go to Authentication > Settings in your Supabase dashboard
2. Enable GitHub provider
3. Add your GitHub OAuth credentials
4. Set up authorized redirect URIs

### 4. Configure Email Settings (Optional)
1. Go to Authentication > Settings
2. Configure SMTP settings for email confirmations
3. Customize email templates if needed

## Features Included

### 🎨 Beautiful UI Design
- Modern glassmorphism design with gradients
- Responsive layout that works on all devices
- Smooth animations and transitions
- Eye-catching floating orbs and visual effects

### 🔐 Authentication Features
- **Email/Password Login**: Secure authentication with form validation
- **User Registration**: Sign up with email verification
- **Social Login**: Google and GitHub OAuth integration
- **Password Reset**: Forgot password functionality
- **Protected Routes**: Automatic redirect to login for unauthorized users
- **User Profile**: Display user information and avatar

### 📱 User Experience
- **Form Validation**: Real-time validation with helpful error messages
- **Loading States**: Beautiful loading animations
- **Password Strength**: Visual password strength indicator
- **Responsive Design**: Works perfectly on mobile and desktop
- **Smooth Transitions**: Elegant page transitions and hover effects

## File Structure
```
frontend/src/
├── components/
│   ├── AuthLayout.js      # Beautiful auth page layout
│   ├── Login.js           # Login form component
│   ├── Signup.js          # Signup form component
│   └── ProtectedRoute.js  # Route protection component
├── contexts/
│   └── AuthContext.js     # Authentication context
└── supabaseClient.js      # Supabase configuration
```

## Usage

### Starting the Application
1. Make sure you've updated the `.env` file with your Supabase credentials
2. Start the frontend development server:
   ```bash
   cd frontend
   npm start
   ```

### Authentication Flow
1. Users will be redirected to the login page if not authenticated
2. New users can click "Sign up" to create an account
3. Existing users can sign in with email/password or social providers
4. Once authenticated, users can access all application features
5. User information is displayed in the navigation panel
6. Users can sign out using the "Sign Out" button

### Routes
- `/login` - Login page
- `/signup` - Signup page
- `/` - Main application (protected)
- `/projects` - Projects page (protected)
- `/cv-builder` - CV builder page (protected)
- `/cv-management` - CV management page (protected)

## Customization

### Styling
The authentication pages use styled-components with a consistent design system. You can customize colors, fonts, and layouts by modifying the styled components in the respective files.

### Authentication Providers
To add more authentication providers, update the `AuthContext.js` file and add corresponding buttons in the login/signup components.

### User Metadata
The signup form collects first name, last name, and email. You can extend this by modifying the signup form and updating the `signUp` function in `AuthContext.js`.

## Security Notes
- Never commit your actual Supabase credentials to version control
- Use environment variables for sensitive configuration
- The anon key is safe to use in client-side code
- Enable Row Level Security (RLS) in Supabase for database operations

## Support
If you encounter any issues:
1. Check the browser console for error messages
2. Verify your Supabase credentials are correct
3. Ensure your Supabase project is active and properly configured
4. Check the Supabase dashboard for authentication logs

## Next Steps
- Set up database tables for storing user-specific CV data
- Implement user profile management
- Add email verification flow
- Set up proper error handling and user feedback
- Configure production deployment settings 