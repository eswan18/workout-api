import React from 'react';
import logo from './logo.svg';
import './App.css';
import Canvas from './Canvas'

// This is essentially just the ever-present frame around the changing canvas
// within the app.
function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Workout App</h1>
        <Canvas/>
        <p>
          Edit <code>src/App.js</code> and save to reload.
        </p>
        <a
          className="App-link"
          href="https://reactjs.org"
          target="_blank"
          rel="noopener noreferrer"
        >
          Learn React
        </a>
      </header>
    </div>
  );
}

export default App;
