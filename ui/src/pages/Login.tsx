import React, { useState } from 'react';
import { login } from '../services/authService';

import './Login.css'
import { useNavigate } from 'react-router-dom';


const Login: React.FC = () => {

  const navigate = useNavigate();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleEmailChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setEmail(event.target.value);
  };

  const handlePasswordChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setPassword(event.target.value);
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const res = await login(email, password)
    if (res.status == 200){
      navigate('/user')
    } else {
      console.log(res)
      // TODO - let user know login was unsuccesful
    }
  }

return (
  <div className='login-container'>
    <div className='login-box'>
      <h2 className='login-title'>Login</h2>
      <form onSubmit={handleSubmit}>
        <div className="input-container">
          <label htmlFor="username">Email:</label>
          <input type="text" id="username" name="username" value={email} onChange={handleEmailChange}/>
        </div>
        <div className="input-container">
          <label htmlFor="password">Password:</label>
          <input type="password" id="password" name="password" value={password} onChange={handlePasswordChange} />
        </div>
        <button type="submit">Login</button>
      </form>
    </div>
  </div>
);
};

export default Login;
