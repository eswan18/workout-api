import React from 'react';
import './App.css';
import AppCanvas from './AppCanvas';
import AppHeader from './AppHeader';
import AppFooter from './AppFooter';

// This is essentially just the ever-present frame around the changing canvas
// within the app.
function App() {
  return (
    <div className="App">
      <AppHeader/>
      <AppCanvas/>
      <AppFooter/>
    </div>
  );
}

export default App;
