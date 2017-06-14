var React = require("react");
var Router = require('react-router');
var Link = Router.Link;
var classNames = require('classnames');
const queryString = require('query-string');

class Logo extends React.Component {
    render() {
        var profileButtonClasses = classNames({
            "glyphicon": true,
            "glyphicon-user": true,
            "profile-button": true,
            "profile-button-active": this.props.routes[this.props.routes.length-1].name == "profile"
        });
        return (
            <div className="logo">
                <Link to="/dashboard/profile/"><span className={profileButtonClasses} title="Profile" onClick={this.props.handleProfile}></span></Link>
                <Link to="/">{this.props.title}</Link>
                <span className="glyphicon glyphicon-off logout-button" title="Logout" onClick={this.props.handleLogout}></span>
            </div>
        )
    }
}

module.exports = Logo;