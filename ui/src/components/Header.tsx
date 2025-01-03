import React from "react";
import { Link } from "react-router-dom";
import "./Header.css";
import { useAuth } from "../contexts/AuthProvider";

const Header: React.FC = () => {
  const auth = useAuth();
  return (
    <header className="header">
      <nav className="nav">
        <ul className="nav-list">
          <li className="nav-item">
            <Link to="/home" className="nav-link">
              Home
            </Link>
          </li>
          <li className="nav-item">
            <Link to="/user" className="nav-link">
              User
            </Link>
          </li>
          <li className="nav-item">
            <Link to="/login" className="nav-link">
              Login
            </Link>
          </li>
          {auth?.token && (
            <li className="nav-item">
              <Link to="" className="nav-link">
                Optional
              </Link>
            </li>
          )}
        </ul>
      </nav>
    </header>
  );
};

export default Header;
