import React from 'react';
import './Home.css'


const Home: React.FC = () => {
  return (
    <div className='home-container'>
      <div className='home-main'>
        <h1 className='title'>Welcome to Our Website!</h1>
        <p className='info'>This is our landing page content. Lorem ipsum dolor sit amet consectetur adipisicing elit. Temporibus necessitatibus sit amet molestiae harum, officiis aliquam perferendis nam eos sed.</p>
      </div>
    </div>
  );
};

export default Home;
