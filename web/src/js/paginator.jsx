var React = require("react");
var Router = require('react-router');
var Link = Router.Link;
var $ = require("jquery");
var classNames = require('classnames');
const queryString = require('query-string');

class Paginator extends React.Component {

    render() {
        var totalPages = Math.ceil(this.props.totalCount/this.props.paginateBy);
        var currentQuery = this.props.app.props.location.query;
        var prevQuery = {};
        var nextQuery = {};
        $.extend(true, prevQuery, currentQuery);
        $.extend(true, nextQuery, currentQuery);
        var prevPage = this.props.currentPage - 1;
        if (prevPage !== 1) {
            prevQuery["p"] = prevPage;
        } else {
            if ("p" in prevQuery) {
                delete prevQuery["p"];
            }
        }
        nextQuery["p"] = this.props.currentPage + 1;

        var prevClasses = classNames({
            'pagination-link': true,
            'pagination-link-prev': true,
            'hidden': !this.props.hasPrev
        });

        var nextClasses = classNames({
            'pagination-link': true,
            'pagination-link-next': true,
            'hidden': !this.props.hasNext
        });

        var paginatorClasses = classNames({
            "pagination": true,
            "hidden": totalPages <= 1
        });

        return (
            <div className={paginatorClasses}>
                <Link to={location.pathname + "?" + queryString.stringify(prevQuery)} className={prevClasses}>
                    previous
                </Link>
                &nbsp;
                <span className="pagination-text">
                    page {this.props.currentPage} of {totalPages}
                </span>
                &nbsp;
                <Link to={location.pathname + "?" + queryString.stringify(nextQuery)} className={nextClasses}>
                    next
                </Link>
            </div>
        )
    }
}

module.exports = Paginator;