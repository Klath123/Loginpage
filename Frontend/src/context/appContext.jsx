import { createContext, useState, useEffect } from "react";
import { toast } from 'react-hot-toast';
import axios from "axios";


export const AppContent = createContext();

export const AppContextProvider = (props) => {
  const backendUrl = import.meta.env.VITE_BACKEND_URL;
  const [isLoggedin, setLoggedIn] = useState(false);
  const [userData, setUserData] = useState(null);

  const getUserData = async () => {
    try {
      const { data } = await axios.get('/api/v1/user/profile', {
        withCredentials: true,
      });
      setUserData(data); 
    } catch (error) {
      const message = error.response?.data?.detail || 'An unexpected error occurred';
      toast.error(message);
      console.error('getUserData error:', message);
    }
  };

  const getAuthState = async () => {
    try {
      const { data } = await axios.get('/api/v1/auth/is-auth', {
        withCredentials: true,
      });

      if (data.auth) {
        setLoggedIn(true);
        await getUserData(); 
      } else {
        setLoggedIn(false);
        setUserData(null);
      }
    } catch (error) {
      const message = error.response?.data?.detail || 'An unexpected error occurred';
      console.error('getAuthState error:', message);
    }
  };


  useEffect(() => {
    getAuthState();
  }, []);


  const value = {
    backendUrl,
    isLoggedin,
    setLoggedIn,
    userData,
    setUserData,
    getUserData,
  };

  return (
    <AppContent.Provider value={value}>
      {props.children}
    </AppContent.Provider>
  );
};
