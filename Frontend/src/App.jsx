import { useState } from 'react'
import './App.css'
import {  Route, Routes } from 'react-router-dom'
import Home from './pages/Home'
import Login from './pages/Login'
import Register from './pages/register'
import EmailVerify from './pages/EmailVerify'
import ResetPassword from './pages/ResetPassword'
import axios from 'axios'
import toast, { Toaster } from 'react-hot-toast';

axios.defaults.baseURL = import.meta.env.VITE_BACKEND_URL;

function App() {
  
  
  return (
    <>
      <Toaster  position="top-center"  toastOptions={{ duration: 5000,removeDelay: 1000, style: {
      background: 'white',
      color: 'black',}}}/>
      <Routes>
        <Route path='/' element={<Home />}></Route>
        <Route path='/register' element={<Register />}></Route>
        <Route path='/email-verify' element={<EmailVerify />}></Route>
        <Route path='/reset-password' element={<ResetPassword />}></Route>
        <Route path='/login' element={<Login />}></Route>
      </Routes>
    </>
  )
}

export default App
