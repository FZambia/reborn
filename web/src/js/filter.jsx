var React = require("react");
var ReactDOM = require('react-dom');
var classNames = require('classnames');
const queryString = require('query-string');


class Filter extends React.Component {

    constructor(props) {
        super(props);
        var query = this.props.app.props.location.query;
        this.state = {
            searchTerm: query["search"] || "",
            favorite: "favorite" in query
        }
    }

    handleFavoriteClick(e) {
        var newFavorite = !this.state.favorite;
        this.setState({favorite: newFavorite});
        var currentQuery = this.props.app.props.location.query;
        if ("p" in currentQuery) {
            delete currentQuery["p"];
        }
        currentQuery["favorite"] = "on";
        if (newFavorite === false) {
            delete currentQuery["favorite"];
        }
        this.props.app.props.router.push(window.location.pathname + "?" + queryString.stringify(currentQuery));
    }

    makeSearch() {
        if (this.searchTimeout) {
            clearTimeout(this.searchTimeout);
        }
        //var name = this.props.app.props.routes.reverse()[0].name;
        var currentQuery = this.props.app.props.location.query;
        if ("p" in currentQuery) {
            delete currentQuery["p"];
        }
        var searchTerm = ReactDOM.findDOMNode(this.refs.search).value;
        currentQuery["search"] = searchTerm;
        if (searchTerm === "") {
            delete currentQuery["search"];
        }
        this.props.app.props.router.push(window.location.pathname + "?" + queryString.stringify(currentQuery));
    }

    handleKeyUp(e) {
        if (e.keyCode === 13) {
            this.makeSearch();
        }
    }

    handleChange(e) {
        this.setState({searchTerm: e.target.value});
        if (this.searchTimeout) {
            clearTimeout(this.searchTimeout);
        }
        this.searchTimeout = setTimeout(function(){
            this.makeSearch();
        }.bind(this), this.props.searchTimeoutMilliseconds);
    }

    render() {
        var classes = classNames({
            "search-favorite": true,
            "glyphicon": true,
            "glyphicon-star-empty": !this.state.favorite,
            "glyphicon-star": this.state.favorite
        });
        return (
            <div className="filter">
                <span className="search-text-container">
                    <input ref="search" className="search-text" type="text" placeholder="search..." value={this.state.searchTerm} onChange={this.handleChange.bind(this)} onKeyUp={this.handleKeyUp.bind(this)} />
                </span>
                <span ref="favorite" className={classes} aria-hidden="true" onClick={this.handleFavoriteClick.bind(this)}>
                </span>
            </div>
        )
    }
}

Filter.defaultProps = {
    searchTimeoutMilliseconds: 200
};

Filter.searchTimeout = undefined;

module.exports = Filter;