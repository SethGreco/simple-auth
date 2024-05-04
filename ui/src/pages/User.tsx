import React from 'react';
import { logout } from '../services/authService';
import { useNavigate } from 'react-router-dom';


const User: React.FC = () => {

  const navigate = useNavigate();

  const handleLogOut = async (event: React.FormEvent<HTMLButtonElement>) => {
    event.preventDefault();
    await logout();
    navigate('/home')
  }
  
  return (
    <div>
      <h1>User Dashboard</h1>
      <p>This is the user page content.</p>
      <button onClick={handleLogOut}>Log Out</button>
    </div>
  );
};

export default User;