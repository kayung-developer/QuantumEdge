import React, { createContext, useState, useEffect, useContext, useCallback } from 'react';
import {
    onAuthStateChanged,
    createUserWithEmailAndPassword,
    signInWithEmailAndPassword,
    signOut,
    GoogleAuthProvider,
    signInWithPopup
} from 'firebase/auth';
import { auth } from 'lib/firebase';
import api from 'services/api';
import SplashScreen from 'components/core/SplashScreen';
import toast from 'react-hot-toast';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const handleAuthSuccess = useCallback(async (firebaseUser) => {
    try {
      const idToken = await firebaseUser.getIdToken(true); // Force refresh

      // Exchange Firebase token for our backend's session tokens
      const { data } = await api.post('/auth/login', { firebase_id_token: idToken });

      localStorage.setItem('accessToken', data.access_token);
      localStorage.setItem('refreshToken', data.refresh_token);

      // After getting our token, fetch the user's profile from our backend
      const profileResponse = await api.get('/users/me');
      setUser(profileResponse.data);

      return profileResponse.data;
    } catch (error) {
      console.error("Backend login or profile fetch failed:", error);
      // Clean up on failure
      setUser(null);
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      await signOut(auth).catch(err => console.error("Firebase signout failed during cleanup:", err));
      throw error; // Re-throw to be caught by the calling function
    }
  }, []);

  const handleSignOut = useCallback(() => {
    setUser(null);
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
  }, []);

  useEffect(() => {
    // This effect runs only once on mount to check the initial auth state
    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
      if (firebaseUser) {
        // User is signed in to Firebase, now let's sync with our backend
        try {
          await handleAuthSuccess(firebaseUser);
        } catch (error) {
            // Handle cases where backend login fails even with a valid Firebase session
            toast.error("Your session could not be verified. Please log in again.");
        }
      } else {
        // User is not signed in to Firebase
        handleSignOut();
      }
      setLoading(false);
    });

    // Cleanup subscription on unmount
    return () => unsubscribe();
  }, [handleAuthSuccess, handleSignOut]);

  // --- Exposed Auth Functions ---

  const register = async (email, password, fullName) => {
    // This flow ensures that if backend registration fails, the Firebase user is deleted.
    let firebaseUser;
    try {
        // First, call our backend to register. It handles Firebase user creation.
        await api.post('/auth/register', { email, password, full_name: fullName });

        // If backend is successful, then sign in with Firebase on the client
        const userCredential = await signInWithEmailAndPassword(auth, email, password);
        firebaseUser = userCredential.user;

        // The onAuthStateChanged listener will then trigger handleAuthSuccess to complete the login
        return firebaseUser;
    } catch (error) {
        console.error("Registration failed:", error);
        // If Firebase user was created by the backend but client-side sign-in failed,
        // we should ideally have a cleanup mechanism, but the backend's error handling
        // already tries to delete the orphaned Firebase user.
        throw error;
    }
  };

  const login = async (email, password) => {
    try {
      await signInWithEmailAndPassword(auth, email, password);
      // onAuthStateChanged will handle the rest of the login flow.
    } catch (error) {
        console.error("Firebase login failed:", error);
        throw error;
    }
  };

  const loginWithGoogle = async () => {
    const provider = new GoogleAuthProvider();
    try {
        await signInWithPopup(auth, provider);
        // onAuthStateChanged will handle the rest of the login flow.
    } catch (error) {
        console.error("Google login failed:", error);
        throw error;
    }
  };

  const logout = async () => {
    try {
      await signOut(auth);
      handleSignOut();
    } catch (error) {
        console.error("Firebase signout failed:", error);
        throw error;
    }
  };

  const value = {
    user,
    isAuthenticated: !!user,
    loading,
    register,
    login,
    loginWithGoogle,
    logout,
  };

  // Render a full-page splash screen only during the initial authentication check.
  if (loading) {
    return <SplashScreen />;
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook to use the auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};