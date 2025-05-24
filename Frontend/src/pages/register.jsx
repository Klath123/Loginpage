import React, { useState,useContext } from 'react';
import axios from 'axios'
import { toast } from 'react-hot-toast'
import { useNavigate, Link}  from 'react-router-dom'
import { AppContent } from '../context/appContext'

function Register() {
  const [data, setData] = useState({ name: '', email: '', password: '' });
  const navigate = useNavigate()
  const {backendUrl,setLoggedIn,getUserData} = useContext(AppContent)

   async function registerUser(e) {
        e.preventDefault()
          try{
            const response = await axios.post('/api/v1/auth/register', data, {
               headers: {
                 'Content-Type': 'application/json'
                },
                withCredentials: true
                });
                if(response.data)
                {
                setLoggedIn(true)
                getUserData()
                toast.success('User registered successfully');
                setData({ name: '', email: '', password: '' });
                navigate('/login')
                }
                 
                
             }
          catch(error){
               const message = error.response?.data?.detail || 'An unexpected error occurred';
               toast.error(message);
              console.log(message)
          }
      }
  return (
    <>
      <div className="container mx-auto px-5 py-4 flex justify-between items-center   my-1 ">
               <Link
                 to="/"
                 className="text-3xl font-bold tracking-tight bg-clip-text"
               >
                 QWI
               </Link>
           </div>
    <div className="flex items-center justify-center px-4">
      <div className="bg-white rounded-xl shadow-lg p-4 w-full max-w-md mt-10 border-2 border-black">
        <h2 className="text-3xl font-bold text-center text-black  mb-6">Create an Account</h2>
        <form onSubmit={registerUser} className="space-y-5">
          <div>
            <label name="name" className="block text-sm font-medium text-black">
              Name:
            </label>
            <input
              type="text"
              id="name"
              placeholder="Enter your name"
              value={data.name}
              onChange={(e) => setData({ ...data, name: e.target.value })}
              required
              className="w-full px-4 py-2 border border-black  rounded-xl focus:outline-none focus:ring-1 "
            />
          </div>
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-black  mb-1">
              Email:
            </label>
            <input
              type="email"
              id="email"
              placeholder="Enter your email"
              value={data.email}
              onChange={(e) => setData({ ...data, email: e.target.value })}
              required
              className="w-full px-4 py-2  border-black border-1 rounded-xl focus:outline-none focus:ring-1"
            />
          </div>
          <div>
            <label name="password" className="block text-sm font-medium text-black  mb-1">
              Password:
            </label>
            <input
              type="password"
              id="password"
              placeholder="Enter your password"
              value={data.password}
              onChange={(e) => setData({ ...data, password: e.target.value })}
              required
              className="w-full px-4 py-2 border-black border-1 rounded-xl focus:outline-none focus:ring-1"
            />
          </div>
           <button
            type="submit"
            className="w-full bg-white  hover:bg-black text-black hover:text-white font-semibold py-2 px-7 border-2 border-black rounded-xl transition duration-"
          >
            Register
          </button>
        </form>
        <p className="mt-4 text-center text-sm text-gray-600 ">
          Already have an account?{' '}
          <Link to="/login" className="text-gray-900 hover:underline">
            Login
          </Link>
        </p>
      </div>
    </div>
    </>
  );
}

export default Register;
