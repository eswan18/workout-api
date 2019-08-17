import './AppCanvas.css';
import React from 'react';
import UserView from './UserView.js'

function AppCanvas () {
  return (
    <div className="AppCanvas">
      <h1>App Canvas</h1>
      <p>App goes here...</p>
      <UserView/>
    </div>
  );
}

export default AppCanvas;
