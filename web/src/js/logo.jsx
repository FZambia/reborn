var React = require("react");
var Router = require('react-router');
var Link = Router.Link;

class Logo extends React.Component {
    render() {
        return (
            <div className="logo">
                <Link to="/">{this.props.title}</Link>
                <span className="glyphicon glyphicon-off logout" title="Logout" onClick={this.props.handleLogout}></span>
            </div>
        )
    }
}

module.exports = Logo;