import React from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../AuthProvider";

const User: React.FC = () => {
  const navigate = useNavigate();
  const auth = useAuth();

  const handleLogOut = async (event: React.FormEvent<HTMLButtonElement>) => {
    event.preventDefault();
    await auth?.logOut();
    navigate("/home");
  };

  return (
    <div>
      <h1>User Dashboard</h1>
      <p>This is the user page content.</p>
      <p>Welcome {auth?.user?.sub}</p>
      <button onClick={handleLogOut}>Log Out</button>
    </div>
  );
};

export default User;
