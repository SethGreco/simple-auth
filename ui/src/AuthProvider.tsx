

// import { useContext, createContext, useState } from "react";
// import { useNavigate } from "react-router-dom";
// import { config } from "./config/config";

// const AuthContext = createContext();

// const AuthProvider = ({ children }) => {
//   const [user, setUser] = useState(null);
//   const [token, setToken] = useState(localStorage.getItem("site") || "");
//   const navigate = useNavigate();
//   const loginAction = async (username: string, password: string) => {
//     try {
//       const response = await fetch(`${config.backendUrl}/login/user/`, {
//         method: "POST",
//         headers: {
//           'Authorization': `Basic ${btoa(`${username}:${password}`)}`,
//           "Content-Type": "application/json",
//         }
//       });
//       const res = await response.json();
//       if (res.data) {
//         setUser(res.data.user);
//         setToken(res.token);
//         localStorage.setItem("site", res.token);
//         navigate("/dashboard");
//         return;
//       }
//       throw new Error(res.message);
//     } catch (err) {
//       console.error(err);
//     }
//   };

//   const logOut = () => {
//     setUser(null);
//     setToken("");
//     localStorage.removeItem("site");
//     navigate("/login");
//   };

//   return (
//     <AuthContext.Provider value={{ token, user, loginAction, logOut }}>
//       {children}
//     </AuthContext.Provider>
//   );

// };

// export default AuthProvider;

// export const useAuth = () => {
//   return useContext(AuthContext);
// };


