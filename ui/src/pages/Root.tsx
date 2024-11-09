import { Outlet } from "react-router-dom";

import Header from "../components/Header";
import React from "react";

const RootLayout: React.FC = () => {
  // const navigation = useNavigation();
  return (
    <>
      <Header />
      <main>
        {/* {navigation.state === 'loading' && <p>Loading...</p>} */}
        <Outlet />
      </main>
    </>
  );
};

export default RootLayout;
