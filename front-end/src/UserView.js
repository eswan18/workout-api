import React from 'react';

class UserView extends React.Component {
  
  constructor (props) {
    super(props);
    // Set the starting state
    this.state = {users: 'eth'};
  }

  componentDidMount() {
    fetch('http://localhost:5000/user/')
    .then(res => res.json())
    .then(json => console.log(json))
  }

  render() {
    return (
      <div className="UserView">
        <h1>Users</h1>
        {this.state.users}
      </div>
    );
  }
}

export default UserView;
