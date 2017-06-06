var React = require("react");
var ReactDOM = require("react-dom");
var $ = require("jquery");
var Router = require('react-router');
var Link = Router.Link;
var classNames = require('classnames');
const queryString = require('query-string');


class SubscriptionRow extends React.Component {
    render() {
        var currentQuery = queryString.parse(location.search);
        var linkClasses = classNames({
            "subscription-link": true,
            "active": location.pathname == "/entry/" && this.props.subscription.id == currentQuery["subscription"]
        });
        var query = {};
        if ("search" in currentQuery) {
            query["search"] = currentQuery["search"];
        }
        if ("favorite" in currentQuery) {
            query["favorite"] = currentQuery["favorite"];
        }
        query["subscription"] = this.props.subscription.id;
        return (
            <li className="subscription">
                <Link to={{pathname: "/entry/", query: query}} ref="link" className={linkClasses}>
                    {this.props.subscription.source.name}
                </Link>
                <Link to={`/subscription/${this.props.provider.id}/${this.props.subscription.id}/edit/`} className="glyphicon glyphicon-cog row-edit"></Link>
            </li>
        );
    }
}

class Provider extends React.Component {
    handleProviderClick(e) {
        var subscriptions = $(ReactDOM.findDOMNode(this.refs.subscriptions));
        subscriptions.toggleClass("subscriptions-hidden");
        var key = "subscriptions_hidden_" + this.props.provider.id;
        if (subscriptions.hasClass("subscriptions-hidden")) {
            localStorage[key] = "1";
        } else {
            localStorage[key] = "0";
        }
        return false;
    }

    handleCreateClick(e) {
        e.stopPropagation();
    }

    render() {
        var rows = [];
        this.props.items.forEach(function (item) {
            rows.push(<SubscriptionRow provider={this.props.provider} subscription={item} key={item.id} />)
        }.bind(this));

        var hiddenKey = "subscriptions_hidden_" + this.props.provider.id;
        var subscriptionsClasses = classNames({
            'subscriptions': true,
            'subscriptions-hidden': localStorage[hiddenKey] === "1"
        });

        return (
            <div ref="provider" className="provider">
                <div className="provider-name" onClick={this.handleProviderClick.bind(this)}>
                    {this.props.provider.name}
                    <Link to={`/subscription/${this.props.provider.id}/create/`} onClick={this.handleCreateClick.bind(this)} className="glyphicon glyphicon-plus-sign row-edit"></Link>
                </div>
                <ul ref="subscriptions" className={subscriptionsClasses}>
                    {rows}
                </ul>
            </div>
        )
    }
}

module.exports = Provider;