import React, { useContext } from 'react';
import background from '../assets/background.png';
import { useNavigate } from 'react-router-dom';
import { AppContent } from '../context/appContext';

function Header() {
  const navigate = useNavigate();
  const { userData } = useContext(AppContent);

  return (
    <header className="flex flex-col items-center justify-center px-4">
      <p className="text-2xl text-center max-w-2xl  mb-10 font-large text-black mt-8">
        {userData ? `${userData.name}!` : "Revolutionize the way you manage queues. Save time, reduce wait stress, and keep things moving smoothly."}
      </p>
      {userData ?``:
      <div
        className="w-full max-w-2xl rounded-xl shadow-2xl p-10 bg-cover bg-center relative"
        style={{ backgroundImage: `url(${background})` }}
      >
        <div className="absolute inset-0 bg-opacity-60 rounded-xl bg-black"></div>
        <div className="relative z-10 text-center">
          <button
            onClick={() => navigate('/register')}
            className="inline-block w-full max-w-sm bg-black text-white font-bold text-lg px-10 py-4 rounded-full shadow-md hover:shadow-xl transform hover:scale-105 transition-all duration-300"
          >
            Get Started
          </button>
        </div>
      </div>
      }
    </header>
  );
}

export default Header;
