var React = require("react");
var Router = require('react-router');
var Link = Router.Link;
const queryString = require('query-string');
var classNames = require('classnames');


class CategoryAllRow extends React.Component {
    render() {
        var className = "category-link";
        if (location.pathname == "/") {
            className += " active";
        }
        var currentQuery = queryString.parse(location.search);
        var query = {};
        if ("search" in currentQuery) {
            query["search"] = currentQuery["search"];
        }
        if ("favorite" in currentQuery) {
            query["favorite"] = currentQuery["favorite"];
        }
        return (
            <li className="category">
                <Link to="/" ref="link" className={className}>
                    {this.props.name}
                </Link>
                <Link to="/category/create/" className="glyphicon glyphicon-plus-sign row-edit"></Link>
            </li>
        );
    }
}

class CategoryRow extends React.Component {
    render() {
        var currentQuery = queryString.parse(location.search);
        var linkClasses = classNames({
            "category-link": true,
            "active": location.pathname == "/entry/" && this.props.id == currentQuery["category"]
        });
        var query = {};
        if ("search" in currentQuery) {
            query["search"] = currentQuery["search"];
        }
        if ("favorite" in currentQuery) {
            query["favorite"] = currentQuery["favorite"];
        }
        query["category"] = this.props.id;
        return (
            <li className="category">
                <Link to={{pathname: "/entry/", query: query}} ref="link" className={linkClasses}>
                    {this.props.name}
                </Link>
                <Link to={`/category/${this.props.id}/edit/`} className="glyphicon glyphicon-cog row-edit"></Link>
            </li>
        );
    }
}

class Category extends React.Component {
    render() {
        var rows = [];
        this.props.items.forEach(function (item, index) {
            rows.push(<CategoryRow id={item.id} name={item.name} index={index} key={item.id} />)
        }.bind(this));
        return (
            <div className="categories-container">
                <ul className="categories">
                    <CategoryAllRow name="Home" />
                    {rows}
                </ul>
            </div>
        )
    }
}

module.exports = Category;