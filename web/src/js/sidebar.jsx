var React = require("react");
var Logo = require("./logo.jsx");
var Category = require("./category.jsx");
var Provider = require("./provider.jsx");

class Sidebar extends React.Component {
    render () {
        var providers = [];
        this.props.providers.forEach(function (item) {
            providers.push(<Provider provider={item} items={item.subscriptions} key={item.name} />)
        }.bind(this));

        return (
            <div className="sidebar">
                <Logo title={this.props.title} handleLogout={this.props.handleLogout} routes={this.props.routes} />
                <Category items={this.props.categories} />
                {providers}
            </div>
        )
    }
}

module.exports = Sidebar;